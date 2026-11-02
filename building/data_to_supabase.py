import os
import json
import psycopg2
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from pgvector.psycopg2 import register_vector

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / "creds" / ".env"

load_dotenv(dotenv_path=ENV_PATH)


DATABASE_URL = os.getenv("DATABASE_URL")

SCRIPT_DIR = Path(__file__).resolve().parent


conn = psycopg2.connect(DATABASE_URL)
register_vector(conn)  # Habilita suporte a vetores (pgvector)


print("Carregando CSVs...")
categories = pd.read_csv(SCRIPT_DIR / "desafio_tecnico_ai_eng - categories.csv")
customers = pd.read_csv(SCRIPT_DIR / "desafio_tecnico_ai_eng - customers.csv")
products = pd.read_csv(SCRIPT_DIR / "desafio_tecnico_ai_eng - products.csv", sep=',', quotechar='"')
orders = pd.read_csv(SCRIPT_DIR / "desafio_tecnico_ai_eng - orders.csv")
order_items = pd.read_csv(SCRIPT_DIR / "desafio_tecnico_ai_eng - order_items.csv")
promotions = pd.read_csv(SCRIPT_DIR / "desafio_tecnico_ai_eng - promotions.csv")

# 6. Insere os dados
with conn.cursor() as cur:
    print("Inserindo categorias...")
    for _, row in categories.iterrows():
        cur.execute(
            "insert into categories (category_id, name, description) values (%s, %s, %s)",
            (row.category_id, row.name, row.description)
        )
    
    print("Inserindo clientes...")
    for _, row in customers.iterrows():
        cur.execute(
            "insert into customers (customer_id, name, phone, email, city) values (%s,%s,%s,%s,%s)",
            (row.customer_id, row.name, row.phone, row.email, row.city)
        )
    
    print("Inserindo produtos...")
    for _, row in products.iterrows():
        cur.execute(
            """insert into products 
               (product_id, name, price_brl, category_id, description, stock_quantity, status, specs, created_at)
               values (%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s)""",
            (row.product_id, row.name, row.price_brl, row.category_id, row.description,
             row.stock_quantity, row.status, row.specs, row.created_at)
        )
    
    print("Inserindo pedidos...")
    for _, row in orders.iterrows():
        cur.execute(
            """insert into orders 
               (order_id, customer_id, order_date, status, total_brl, payment_method, tracking_code, estimated_delivery, notes)
               values (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (row.order_id, row.customer_id, row.order_date, row.status, row.total_brl,
             row.payment_method, row.tracking_code if pd.notna(row.tracking_code) else None,
             row.estimated_delivery if pd.notna(row.estimated_delivery) else None,
             row.notes if pd.notna(row.notes) else None)
        )
    
        # Order items
    print("Inserindo itens dos pedidos...") # (já deve estar no seu)
    for row in order_items.to_dict(orient="records"):
        cur.execute(
            "insert into order_items (order_id, product_id, quantity) values (%s,%s,%s)",
            (row["order_id"], row["product_id"], row["quantity"])
        )
    
        # Promotions
    print("Inserindo promoções...") # (já deve estar no seu)
    for row in promotions.to_dict(orient="records"):
        cur.execute(
            "insert into promotions (promotion_id, product_id, discount_percent, description, is_active) values (%s,%s,%s,%s,%s)",
            (row["promotion_id"], row["product_id"], row["discount_percent"], row["description"], bool(row["is_active"]))
        )

# 7. Salva tudo
conn.commit()
conn.close()
print("🎉 Dados carregados com sucesso!")