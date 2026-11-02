import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
from openai import OpenAI
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import time

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / "creds" / ".env"
load_dotenv(dotenv_path=ENV_PATH)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# --- CAMINHO ABSOLUTO E DIRETO ---
PDF_PATH = Path(r"C:\Users\Dell\Documents\Emporio da Musica\tools\politicas_da_loja.pdf")

def extrair_texto_pdf():
    print(f"Procurando arquivo em: {PDF_PATH}")
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"❌ O arquivo NÃO EXISTE no caminho especificado. Verifique se o nome está exato.")
    
    print("✅ Arquivo encontrado! Lendo PDF...")
    reader = PdfReader(PDF_PATH)
    texto_completo = ""
    for page in reader.pages:
        texto_completo += page.extract_text() + "\n"
    return texto_completo

def processar_e_salvar():
    texto = extrair_texto_pdf()
    print(f"Texto extraído: {len(texto)} caracteres.")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = splitter.split_text(texto)
    print(f"Dividido em {len(chunks)} chunks.")

    batch_size = 20
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        try:
            resp = openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=batch
            )
            dados = []
            for j, chunk in enumerate(batch):
                dados.append({
                    "content": chunk,
                    "embedding": resp.data[j].embedding,
                    "metadata": {"source": "politicas_da_loja.pdf"}
                })
            supabase.table("policy_chunks").insert(dados).execute()
            print(f"✅ Lote {i//batch_size + 1} inserido no Supabase.")
            time.sleep(1)
        except Exception as e:
            print(f"❌ Erro no lote {i//batch_size + 1}: {e}")

    print("🎉 Políticas processadas com sucesso!")

if __name__ == "__main__":
    processar_e_salvar()