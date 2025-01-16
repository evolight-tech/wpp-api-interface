import streamlit as st
from utils.api_client import call_api
from dotenv import load_dotenv
import os

load_dotenv(override=True)
SENHA = os.getenv("SENHA")

# Configuração inicial
st.set_page_config(page_title="Gerenciador de API", layout="wide",initial_sidebar_state="collapsed")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Exibir "popup" para autenticação
if not st.session_state.authenticated:
    placeholder = st.empty()  # Espaço reservado para o "popup"
    with placeholder.container():
        st.title("Autenticação")
        st.write("Insira a senha para acessar o aplicativo.")
        senha = st.text_input("Senha", type="password", key="password")

        if st.button("Entrar"):
            if senha == SENHA:
                st.session_state.authenticated = True
                st.success("Acesso liberado!")
                placeholder.empty()  # Remove o "popup"
                st.rerun()  # Recarrega a página
            else:
                st.error("Senha incorreta.")

# Conteúdo do app, mostrado apenas após a autenticação
if st.session_state.authenticated:
    # Função para verificar conversas ativas
    def verificar_conversas_ativas():
        contatos = call_api("/contatos", method="GET")  # Substitua pelo endpoint correto
        nenhuma = True
        for contato in contatos:
            if contato["em_conversa"] == 1:
                st.warning(f"Conversa ativa no setor {contato['setor']}")
                nenhuma = False
        if nenhuma:
            st.info("Nenhuma conversa ativa.")

    # Botão para verificar conversas ativas
    if st.button("Verificar Conversas Ativas"):
        verificar_conversas_ativas()

    # Sidebar para navegação
    menu = st.sidebar.selectbox(
        "Selecione a seção",
        ["Contatos", "FAQ", "EVO", "Eventos", "Conversas", "Fila"],
        index=0
    )

    # Roteamento para páginas
    if menu == "Contatos":
        from paginas import contatos
        contatos.render()
    elif menu == "FAQ":
        from paginas import faq
        faq.render()
    elif menu == "EVO":
        from paginas import evo
        evo.render()
    elif menu == "Conversas":
        from paginas import conversas
        conversas.render()
    elif menu == "Fila":
        from paginas import fila
        fila.render()
    elif menu == "Eventos":
        from paginas import eventos
        eventos.render()
