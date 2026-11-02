import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Carrega credenciais
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / "creds" / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") # Secret key

# URL da função (garanta que o nome bate com o painel do Supabase)
FUNCTION_URL = f"{SUPABASE_URL}/functions/v1/hybrid_search_policies"

headers = {
    "apikey": SUPABASE_KEY,  # <-- APENAS a chave, sem "Bearer"
    "Content-Type": "application/json"
}

payload = {
    "query": "Quais são as formas de pagamento?",
    "limite": 3
}

print("Chamando Edge Function...")
response = requests.post(FUNCTION_URL, headers=headers, json=payload)

if response.status_code == 200:
    print("✅ Sucesso!")
    import json
    dados = response.json()
    for i, candidato in enumerate(dados.get("candidatos", [])):
        print(f"\n--- Trecho {i+1} (Score: {candidato.get('score'):.4f}) ---")
        print(candidato.get("content")[:300] + "...")
else:
    print(f"❌ Erro {response.status_code}: {response.text}")