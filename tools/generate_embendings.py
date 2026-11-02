import os
import time
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
from openai import OpenAI

# --- Configuração de caminhos e credenciais ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / "creds" / ".env"
load_dotenv(dotenv_path=ENV_PATH)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") # Use a service_role key!
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def gerar_embeddings():
    print("Buscando produtos sem embedding...")
    
    # Busca apenas os produtos que ainda não têm embedding
    response = supabase.table("products").select("product_id, name, description").is_("embedding", "null").execute()
    produtos = response.data
    
    if not produtos:
        print("Todos os produtos já possuem embeddings!")
        return

    print(f"Encontrados {len(produtos)} produtos para processar.")
    
    # Processa em lotes de 20 para evitar limites de taxa da API
    batch_size = 20
    for i in range(0, len(produtos), batch_size):
        batch = produtos[i:i+batch_size]
        
        # Prepara os textos combinando nome e descrição
        textos = [f"{p['name']}. {p['description']}" for p in batch]
        
        try:
            # Chama a OpenAI
            resp = openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=textos
            )
            
            # Atualiza cada produto no Supabase
            for j, p in enumerate(batch):
                embedding = resp.data[j].embedding
                
                # O SDK do Supabase aceita listas (o pgvector entende como vetor)
                supabase.table("products").update({"embedding": embedding}).eq("product_id", p['product_id']).execute()
                
            print(f"✅ Lote {i//batch_size + 1} processado ({len(batch)} produtos).")
            
            # Pequena pausa para evitar rate limit
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Erro no lote {i//batch_size + 1}: {e}")

    print("🎉 Embeddings gerados com sucesso!")


gerar_embeddings()