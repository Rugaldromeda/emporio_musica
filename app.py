import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
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

# Inicializa o histórico de mensagens do Streamlit (para exibição)
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🎵 Empório da Música")
st.caption("Olá! 👋 Sou o assistente do Emporio da Musica. Como posso ajudar?")

# Sidebar
with st.sidebar:
    st.header("Opções")
    if st.button("🗑️ Limpar conversa", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Renderiza o histórico visual
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🎵"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Input do chat
if prompt := st.chat_input("Digite sua pergunta..."):
    # Adiciona a mensagem do usuário ao histórico visual
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Chama o agente
    with st.chat_message("assistant", avatar="🎵"):
        with st.spinner("Consultando..."):
            try:
                # 1. Converte o histórico visual para o formato de mensagens do LangChain
                # A API nova espera uma lista de objetos HumanMessage e AIMessage
                mensagens_langchain = []
                
                # Pega todo o histórico exceto a última mensagem (que já está no prompt)
                for m in st.session_state.messages[:-1]:
                    if m["role"] == "user":
                        mensagens_langchain.append(HumanMessage(content=m["content"]))
                    else:
                        mensagens_langchain.append(AIMessage(content=m["content"]))
                
                # Adiciona a pergunta atual do usuário
                mensagens_langchain.append(HumanMessage(content=prompt))
                
                # 2. Invoca o agente passando a lista de mensagens
                resposta = st.session_state.agente.invoke({
                    "messages": mensagens_langchain
                })
                
                # 3. A resposta final é a última mensagem na lista retornada
                output = resposta["messages"][-1].content
                st.markdown(output)
                
            except Exception as e:
                st.error(f"Erro: {e}")
                output = "Desculpe, tive um problema. Tente novamente."
    
    # Adiciona a resposta do agente ao histórico visual
    st.session_state.messages.append({"role": "assistant", "content": output})