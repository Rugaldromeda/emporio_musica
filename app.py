import streamlit as st
import os
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI
from pathlib import Path

st.set_page_config(
    page_title="Emporio da Musica - Assistente",
    page_icon="🎵",
    layout="centered",  # ou "wide"
)

st.title("🎵 Emporio da Musica")
st.caption("Seu assistente virtual de música")

dotenv_path = Path(__file__).parent / "creds" / ".env"

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! 👋 Sou o assistente do Emporio da Musica. Como posso ajudar?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Pergunte algo sobre instrumentos, partituras, pedidos, etc..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})

with st.sidebar:
    st.header("Opções")
    if st.button("🗑️ Limpar conversa"):
        st.session_state.messages = []
        st.rerun()