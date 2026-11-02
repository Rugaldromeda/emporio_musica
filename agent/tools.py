import os
import json
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
from langchain_core.tools import tool

# Carrega credenciais
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / "creds" / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@tool
def buscar_produtos(query: str) -> str:
    """Busca produtos no catálogo da Empório da Música. Use quando o cliente perguntar sobre modelos, preços, marcas ou recomendações de instrumentos."""
    try:
        response = supabase.functions.invoke(
            "hybrid_search_products", 
            invoke_options={"body": {"query": query, "limite": 5}}
        )
        if response.data:
            return json.dumps(response.data.get("candidatos", []), ensure_ascii=False)
        return "Nenhum produto encontrado."
    except Exception as e:
        return f"Erro ao buscar produtos: {e}"

@tool
def buscar_politicas(query: str) -> str:
    """Busca informações nas políticas da loja (horários, devoluções, formas de pagamento, garantias, frete). Use para dúvidas sobre regras e procedimentos."""
    try:
        response = supabase.functions.invoke(
            "hybrid_search_policies", 
            invoke_options={"body": {"query": query, "limite": 3}}
        )
        if response.data:
            return json.dumps(response.data.get("candidatos", []), ensure_ascii=False)
        return "Nenhuma política encontrada."
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