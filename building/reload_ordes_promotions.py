import os
import psycopg2
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

# Carrega .env
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / "creds" / ".env")
DB_URL = os.getenv("DATABASE_URL")

# Conecta
conn = psycopg2.connect(DB_URL)

# Caminhos dos CSVs (ajustados para os nomes que você renomeou)
TOOLS_DIR = PROJECT_ROOT / "building"
orders_csv = TOOLS_DIR / "desafio_tecnico_ai_eng - orders.csv"
order_items_csv = TOOLS_DIR / "desafio_tecnico_ai_eng - order_items.csv"
promotions_csv = TOOLS_DIR / "desafio_tecnico_ai_eng - promotions.csv"

# Lendo os arquivos
orders = pd.read_csv(orders_csv, quotechar='"', skipinitialspace=True)
order_items = pd.read_csv(order_items_csv, quotechar='"', skipinitialspace=True)
promotions = pd.read_csv(promotions_csv, quotechar='"', skipinitialspace=True)

with conn.cursor() as cur:
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
    
        print("Inserindo itens dos pedidos...")
    for _, row in order_items.iterrows():
        cur.execute(
            "insert into order_items (order_id, product_id, quantity) values (%s,%s,%s)",
            # Forçando a conversão para int() nativo do Python
            (int(row.order_id), int(row.product_id), int(row.quantity))
        )

    print("Inserindo promoções...")
    for _, row in promotions.iterrows():
        cur.execute(
            "insert into promotions (promotion_id, product_id, discount_percent, description, is_active) values (%s,%s,%s,%s,%s)",
            # Forçando a conversão
            (int(row.promotion_id), int(row.product_id), float(row.discount_percent), row.description, bool(row.is_active))
        )

conn.commit()
conn.close()
print("🎉 Pedidos, itens e promoções recarregados com sucesso!")