import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Como o script está em testing/, voltamos DUAS pastas para achar a raiz
PROJECT_ROOT = Path(__file__).resolve().parent.parent 
load_dotenv(dotenv_path=PROJECT_ROOT / "creds" / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Verificação de segurança para não dar o erro de None de novo
if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERRO: Variáveis de ambiente não carregadas. Verifique o caminho do .env.")
    exit(1)

url = f"{SUPABASE_URL}/functions/v1/dynamic-function"

headers = {
    "apikey": SUPABASE_KEY,
    "Content-Type": "application/json"
}

payload = {
    "query": "violão clássico até 1000 reais",
    "limite": 3
}

print(f"Testando URL: {url}")
response = requests.post(url, headers=headers, json=payload)
print(f"Status: {response.status_code}")
print(f"Resposta: {response.text}")