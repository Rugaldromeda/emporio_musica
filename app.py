import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from agent.graph import criar_agente

# Configuração da página
st.set_page_config(
    page_title="Emporio da Musica - Assistente",
    page_icon="🎵",
    layout="centered",
)

# Carrega o .env
dotenv_path = Path(__file__).parent / "creds" / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Inicializa o agente (guardamos no session_state para não recriar a cada rerun)
if "agente" not in st.session_state:
    st.session_state.agente = criar_agente()

# Inicializa o histórico
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🎵 Emporio da Musica")
st.caption("Assistente virtual — pergunte o que quiser!")

# Sidebar
with st.sidebar:
    st.header("Opções")
    if st.button("🗑️ Limpar conversa", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Renderiza o histórico
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🎵"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Input do chat
if prompt := st.chat_input("Digite sua pergunta..."):
    # Adiciona a mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    # Chama o agente
    with st.chat_message("assistant", avatar="🎵"):
        with st.spinner("Consultando o banco..."):
            try:
                # O LangChain precisa do histórico no formato (human, ai)
                chat_history = []
                for m in st.session_state.messages[:-1]: # Exclui a mensagem atual
                    chat_history.append(("human" if m["role"] == "user" else "ai", m["content"]))
                
                # Executa o agente
                resposta = st.session_state.agente.invoke({
                    "input": prompt,
                    "chat_history": chat_history
                })
                output = resposta["output"]
                st.markdown(output)
                
            except Exception as e:
                st.error(f"Erro: {e}")
                output = "Desculpe, tive um problema. Tente novamente."
    
    # Adiciona a resposta do agente ao histórico
    st.session_state.messages.append({"role": "assistant", "content": output})