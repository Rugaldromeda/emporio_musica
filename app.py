import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# ---------- CONFIG ----------
st.set_page_config(
    page_title="Emporio da Musica - Assistente",
    page_icon="🎵",
    layout="centered",
)

# ---------- ENV ----------
dotenv_path = Path(__file__).parent / "creds" / ".env"
load_dotenv(dotenv_path=dotenv_path)
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

SYSTEM_PROMPT = (
    "Você é o assistente virtual do Emporio da Musica. "
    "Responda em português do Brasil, de forma amigável e objetiva. "
    "Ajude com dúvidas sobre instrumentos, partituras e serviços da loja."
)

# ---------- ESTADO ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- HEADER ----------
st.title("🎵 Emporio da Musica")
st.caption("Assistente virtual — pergunte o que quiser!")

# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("Opções")
    if st.button("🗑️ Limpar conversa", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ---------- HISTÓRICO ----------
for message in st.session_state.messages:
    avatar = "🧑" if message["role"] == "user" else "🎵"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# ---------- INPUT ----------
if prompt := st.chat_input("Digite sua pergunta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🎵"):
        try:
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                ],
                stream=True,
            )
            response = st.write_stream(stream)
        except Exception as e:
            st.error(f"Erro: {e}")
            response = "Desculpe, tive um problema. Tente novamente."
    st.session_state.messages.append({"role": "assistant", "content": response})