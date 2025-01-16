import streamlit as st
from time import sleep
from datetime import datetime
import pandas as pd
from utils.api_client import call_api
import zipfile
import io

def extrair_data(arquivo):
    try:
        # Divide o nome pelos underscores e extrai a parte correspondente à data e hora
        partes = arquivo.split("_")
        data_hora_str = partes[-2] + " " + partes[-1].replace(".txt", "")  # Junta data e hora e remove a extensão
        return datetime.strptime(data_hora_str, "%Y-%m-%d %H-%M-%S")  # Novo formato com hífens e traços
    except Exception as e:
        st.warning(f"Erro ao extrair data de {arquivo}: {e}")
        return datetime.min 

def render():
    st.title("EVO")
    with st.expander("Sobre esta página:"):
        st.write("""
            Esta seção está relacionada à leitura das conversas da EVO com clientes pelo WhatsApp.\n
            Aqui é possível verificar as conversas em andamento e fazer o download das conversas do mês atual.\n
            As conversas dos meses anteriores estarão disponíveis para download na pasta do Google Drive: https://drive.google.com/drive/folders/16CexjYXLVNtOmJK_xrLmcjTinPOH3a60?usp=drive_link.\n
            \n\n
            Funções disponíveis:
            - Ver Chats: Lista todos os chats cadastrados. Se o "status" do chat for igual a 0, significa que a conversa está em andamento naquele instante.
            - Listar Conversas: Exibe os arquivos das conversas realizadas no formato .txt.
            - Remover Chat: Remove o registro de uma conversa.
        """)
    option = st.selectbox("Escolha uma ação:", ["Ver Chats", "Listar Conversas", "Remover Chat"])
    
    if option == "Ver Chats":
        if st.button("Listar Chats"):
            response = call_api("/chat", method="GET")
            if response and isinstance(response, list):  # Verifica se a resposta é uma lista
                if len(response) > 0:
                    # Converte a resposta em um DataFrame para exibir como tabela
                    df = pd.DataFrame(response)
                    df.reset_index(drop=True, inplace=True)
                    st.dataframe(df,hide_index=True)  # Exibição como tabela interativa
                else:
                    st.info("Nenhum chat encontrado.")
            else:
                st.warning("Nenhum chat encontrado.")
    
    elif option == "Listar Conversas":
        response = call_api("/history", method="GET")
        if response and isinstance(response, list):
            if len(response) > 0:
                response.sort(key=extrair_data, reverse=True) # Ordena os arquivos por data
                st.write("Lista de Arquivos:")
                
                # Itera sobre os arquivos para criar a tabela personalizada
                for index, arquivo in enumerate(response):
                    col1, col2, col3 = st.columns([3, 1, 1])  # Define o layout das colunas
                    arquivo_display = arquivo.replace("_", " ")
                    col1.write(arquivo_display)
                    if col2.download_button(
                        label="Baixar",
                        data=call_api(f"/history/{arquivo}", method="GET"),  # Obtém o conteúdo diretamente
                        file_name=arquivo,  # Nome do arquivo para download
                        mime="text/plain",  # Tipo MIME do arquivo
                        key=f"baixar-{index}"
                    ):
                        st.success("Download concluído.")

                    if col3.button("Apagar", key=f"apagar-{index}",type="primary"):
                        response = call_api(f"/history/{arquivo}", method="DELETE")
                        st.error(f"Arquivo apagado: {arquivo}")
                        sleep(1)
                        st.rerun()
            else:
                st.info("Nenhuma conversa encontrada.")
        else:
            st.warning("Nenhuma conversa encontrada.")

        st.markdown("<hr>", unsafe_allow_html=True)
        # Botões para ações gerais
        col1, col2, col3 = st.columns([1, 1, 1])

        # Botão para baixar todos os arquivos
        with col1:
            if st.button("Baixar Todos os Arquivos", type="secondary"):
                # Cria um arquivo ZIP com todos os arquivos
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                    for arquivo in response:
                        file_data = call_api(f"/history/{arquivo}", method="GET")  # Obtém o conteúdo de cada arquivo
                        zip_file.writestr(arquivo, file_data)  # Adiciona ao ZIP
                zip_buffer.seek(0)
                
                # Exibe o botão para download do ZIP
                st.download_button(
                    label="Clique aqui para baixar o ZIP",
                    data=zip_buffer,
                    file_name="todos_arquivos.zip",
                    mime="application/zip",
                )

        # Botão para apagar todos os arquivos
        with col3:
            if not st.session_state.get("confirmar_apagar_tudo", False):
                if st.button("Apagar Todos os Arquivos", type="primary"):
                    st.session_state.confirmar_apagar_tudo = True

            if st.session_state.get("confirmar_apagar_tudo", False):
                st.warning("Tem certeza de que deseja apagar TODOS os arquivos? Esta ação não pode ser desfeita.")
                
                col_confirmar, col_cancelar = st.columns(2)
                with col_confirmar:
                    if st.button("Sim, apagar tudo", key="confirmar_apagar"):
                        # Chama a rota para apagar todos os arquivos
                        response = call_api("/history", method="DELETE")
                        if response:  # Verifica se a resposta é bem-sucedida
                            st.success("Todos os arquivos foram apagados com sucesso!")
                            st.session_state.confirmar_apagar_tudo = False
                            sleep(1)
                            st.rerun()
                        else:
                            st.error("Ocorreu um erro ao apagar os arquivos.")
                with col_cancelar:
                    if st.button("Não, cancelar", key="cancelar_apagar"):
                        st.session_state.confirmar_apagar_tudo = False
                        st.info("Ação cancelada.")
                    
    
    elif option == "Remover Chat":
        faq_id = st.text_input("ID do Chat")
        data = {'id': faq_id}
        if st.button("Remover Chat"):
            response = call_api(f"/chat", method="DELETE", data=data)
            st.json(response)
