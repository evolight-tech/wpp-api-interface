import streamlit as st
import pandas as pd
from utils.api_client import call_api


def render():
    st.title("Contatos")
    with st.expander("Sobre esta página:"):
        st.write(
            """
            Esta seção está relacionada ao gerenciamento dos contatos dos responsáveis pelos diferentes setores de comunicação disponíveis no canal do WhatsApp.
            \n\n
            Funções disponíveis:
            - Ver Contatos: Lista todos os contatos cadastrados, seus setores e mostra se estão em conversa com algum cliente.
            - Atualizar Contato: Atualiza as informações de um contato existente.
            - Definir Disponibilidade: Define a disponibilidade de um contato para atendimento.
            - Encerrar Conversa: Encerra a conversa com um cliente forçadamente. Usado para casos de eventuais problemas técnicos.
            - Adicionar Contato: Adiciona um novo contato.
            - Remover Contato: Remove um contato existente.
        """
        )
    response = call_api("/contatos", method="GET")
    contatos = []
    setores = []
    if response and isinstance(response, list):  # Verifica se a resposta é uma lista
        if len(response) > 0:
            for contato in response:
                contatos.append(contato)
                setores.append(contato["setor"])

    option = st.selectbox(
        "Escolha uma ação:",
        [
            "Ver Contatos",
            "Atualizar Contato",
            "Definir Disponibilidade",
            "Encerrar Conversa",
            "Adicionar Contato",
            "Remover Contato",
        ],
    )

    if option == "Ver Contatos":
        if st.button("Listar Contatos"):
            response = call_api("/contatos", method="GET")
            if response and isinstance(
                response, list
            ):  # Verifica se a resposta é uma lista
                if len(response) > 0:
                    # Converte a resposta em um DataFrame para exibir como tabela
                    df = pd.DataFrame(response)
                    df.reset_index(drop=True, inplace=True)
                    # Mapeia os valores da coluna 'disponivel'
                    if "disponivel" in df.columns:
                        df["disponivel"] = df["disponivel"].map(
                            {True: "Indisponível", False: "Disponível"}
                        )

                    # Reordenar colunas
                    colunas_ordenadas = [
                        "setor",
                        "nome_responsavel",
                        "telefone_responsavel",
                        "nome_cliente",
                        "telefone_cliente",
                        "em_conversa",
                        "disponivel",
                        "subtopicos",
                    ]
                    df = df[colunas_ordenadas]
                    st.dataframe(df, hide_index=True)  # Exibição como tabela interativa
                else:
                    st.info("Nenhum contato cadastrado.")
            else:
                st.error("Nenhum contato cadastrado.")

    elif option == "Atualizar Contato":
        # TODO - Separar os campos dos subtópicos
        setor = st.selectbox("Setor", setores)
        telefone_responsavel = st.text_input(
            "Telefone do Responsável",
            value=contatos[setores.index(setor)]["telefone_responsavel"],
        )
        nome_responsavel = st.text_input(
            "Nome do Responsável",
            value=contatos[setores.index(setor)]["nome_responsavel"],
        )
        subtopicos = st.text_area(
            "Subtópicos",
            placeholder="Subtópico 1,Subtópico 2,Subtópico 3,Subtópico 4",
            value=contatos[setores.index(setor)]["subtopicos"],
        )
        data = {
            "setor": setor,
            "telefone_responsavel": telefone_responsavel,
            "nome_responsavel": nome_responsavel,
            "subtopicos": subtopicos,
        }
        if st.button("Atualizar Contato"):
            response = call_api(f"/contatos", method="PUT", data=data)
            st.json(response)

    elif option == "Definir Disponibilidade":
        setor = st.selectbox("Setor", setores)
        disponibilidade = st.selectbox(
            "Disponibilidade", ["Disponível", "Indisponível"]
        )
        disponibilidade = 1 if disponibilidade == "Indisponível" else 0
        data = {"setor": setor, "disp": disponibilidade}
        if st.button("Definir Disponibilidade"):
            response = call_api(f"/contatos/disp", method="PATCH", data=data)
            st.json(response)

    elif option == "Encerrar Conversa":
        telefone_responsavel = st.text_input(
            "Telefone do Responsável", placeholder="556298299370"
        )
        data = {"telefone_responsavel": telefone_responsavel}
        if st.button("Encerrar Conversa"):
            response = call_api(f"/contatos", method="PATCH", data=data)
            st.json(response)

    elif option == "Adicionar Contato":
        # TODO - Separar os campos dos subtópicos
        setor = st.text_input("Setor")
        telefone_responsavel = st.text_input(
            "Telefone do Responsável", placeholder="556298299370"
        )
        nome_responsavel = st.text_input("Nome do Responsável")
        subtopicos = st.text_area(
            "Subtópicos", placeholder="Subtópico 1,Subtópico 2,Subtópico 3,Subtópico 4"
        )
        data = {
            "setor": setor,
            "telefone_responsavel": telefone_responsavel,
            "nome_responsavel": nome_responsavel,
            "subtopicos": subtopicos,
        }
        if st.button("Adicionar Contato"):
            response = call_api(f"/contatos", method="POST", data=data)
            st.json(response)

    elif option == "Remover Contato":
        setor = st.text_input("Setor")
        data = {"setor": setor}
        if st.button("Remover Contato"):
            response = call_api(f"/contatos", method="DELETE", data=data)
            st.json(response)
