import os
import json
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import requests
from supabase import create_client, Client
from langchain_core.tools import tool

# Tenta carregar o .env local (só funciona na sua máquina)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / "creds" / ".env")

def get_secret(key):
    
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError):
        return os.getenv(key)

SUPABASE_URL = get_secret("SUPABASE_URL")
SUPABASE_KEY = get_secret("SUPABASE_KEY")
OPENAI_API_KEY = get_secret("OPENAI_API_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

@tool
def buscar_produtos(query: str) -> str:
    """Busca produtos no catálogo da Empório da Música. Use quando o cliente perguntar sobre modelos, preços, marcas ou recomendações de instrumentos."""
    try:
        # 1. Gera o embedding da pergunta usando a OpenAI
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=query,
            dimensions=1536
        )
        embedding = response.data[0].embedding

        # 2. Chama a função SQL diretamente no banco via RPC
        result = supabase.rpc("hybrid_search_products", {
            "query_text": query,
            "query_embedding": embedding,
            "match_count": 15
        }).execute()

        # 3. Retorna os dados
        if result.data:
            return json.dumps(result.data, ensure_ascii=False)
        return "Nenhum produto encontrado."
        
    except Exception as e:
        return f"Erro ao buscar produtos: {e}"

@tool
def buscar_politicas(query: str) -> str:
    """Busca informações nas políticas da loja, regras de devolução, formas de pagamento, garantias, frete, horários de funcionamento, endereço e telefone. Use para dúvidas sobre regras, procedimentos e informações de contato."""
    try:
        # Usando requests em vez do SDK para evitar erros de autenticação
        url = f"{SUPABASE_URL}/functions/v1/hybrid_search_policies"
        headers = {
            "apikey": SUPABASE_KEY,
            "Content-Type": "application/json"
        }
        payload = {"query": query, "limite": 10}
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            dados = response.json()
            if dados.get("candidatos"):
                return json.dumps(dados["candidatos"], ensure_ascii=False)
            return "Nenhuma política encontrada."
        else:
            return f"Erro na Edge Function: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Erro ao buscar políticas: {e}"

@tool
def consultar_banco(sql_query: str) -> str:
    """Consulta dados estruturados (pedidos, clientes, promoções) usando SQL. 
    REGRAS: Só use SELECT. Tabelas e colunas:
    - orders (order_id, customer_id, order_date, status, total_brl, payment_method, tracking_code, estimated_delivery, notes)
    - order_items (order_id, product_id, quantity)
    - products (product_id, name, price_brl, stock_quantity, status)
    - customers (customer_id, name, email, city)
    - promotions (promotion_id, product_id, discount_percent, is_active)"""
    query_upper = sql_query.strip().upper()
    if not query_upper.startswith("SELECT"):
        return "Erro: Apenas SELECT é permitido."
    forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "CREATE", "GRANT"]
    if any(f" {word} " in f" {query_upper} " for word in forbidden):
        return "Erro: Comando não permitido."
    try:
        response = supabase.rpc("executar_select_seguro", {"query_sql": sql_query}).execute()
        if response.data:
            return json.dumps(response.data, ensure_ascii=False)
        return "Nenhum resultado."
    except Exception as e:
        return f"Erro ao executar SQL: {e}"