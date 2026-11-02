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

# O pulo do gato: ler o CSV com parâmetros corretos para não bagunçar as colunas
csv_path = PROJECT_ROOT / "building" / "desafio_tecnico_ai_eng - products.csv"
df = pd.read_csv(csv_path, quotechar='"', skipinitialspace=True)

with conn.cursor() as cur:
    for _, row in df.iterrows():
        cur.execute(
            """insert into products 
               (product_id, name, price_brl, category_id, description, stock_quantity, status, specs, created_at)
               values (%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s)""",
            (row.product_id, row['name'], row.price_brl, row.category_id, row.description,
             row.stock_quantity, row.status, row.specs, row.created_at)
        )

conn.commit()
conn.close()
print("🎉 Produtos recarregados com sucesso!")