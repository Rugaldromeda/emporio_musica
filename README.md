# 🎸 Empório da Música - Agente de Atendimento AI

Este projeto é um agente de atendimento virtual construído em Python com Streamlit, utilizando LangChain e OpenAI para roteamento de ferramentas (Tool Calling), e Supabase (PostgreSQL + pgvector) como banco de dados.

## 🚀 Como rodar o projeto

### Pré-requisitos

- Python 3.10+
- Conta no Supabase
- Chave de API da OpenAI

### 1. Configuração do ambiente

```bash
git clone https://github.com/seu-usuario/emporio-da-musica.git
cd emporio-da-musica
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate no Windows
pip install -r requirements.txt
```

### 2. Variáveis de Ambiente

Crie um arquivo `.env` na pasta `creds/` com:

```env
SUPABASE_URL="https://seu-projeto.supabase.co"
SUPABASE_KEY="sua-chave-secreta-aqui"
OPENAI_API_KEY="sua-chave-openai-aqui"
DATABASE_URL="postgresql://..." # Apenas para os scripts de ETL
```

### 3. Rodando o Agente

```bash
streamlit run app.py
```

---

## 🧠 Decisões Técnicas e Justificativas

### 1. Framework: LangChain (v1.x) e Streamlit

- **Streamlit:** Escolhido pela agilidade na criação de interfaces de chat. Ele permite prototipar um frontend funcional em poucas linhas, sem a necessidade de construir um app React/Next.js complexo para uma prova de conceito.
- **LangChain:** Utilizado pela abstração madura de **Tool Calling**. A versão moderna (`create_agent`) permite que o LLM decida dinamicamente qual ferramenta usar, mantendo a memória da conversa e o histórico de forma simples.

### 2. LLM: `gpt-4o-mini`

- **Justificativa:** É um modelo extremamente rápido, com um custo-benefício excelente para atendimento ao cliente. Ele possui uma janela de contexto grande o suficiente para as regras e o histórico, e a capacidade de _function calling_ (chamar ferramentas) é muito precisa para o nosso escopo.

### 3. Arquitetura de Retrieval: RAG Híbrido

Para a busca de produtos e políticas, não utilizamos apenas busca vetorial. Implementamos um **RAG Híbrido** diretamente no PostgreSQL:

- **Busca Vetorial (`pgvector`):** Resolve o problema de vocabulário (ex: o cliente busca "instrumento de cordas macias" e encontra "violão de nylon").
- **Full-Text Search (`tsvector`):** Garante que termos exatos não se percam (ex: "PIX", "12x", nomes de modelos como "Takamine GD20").
- **RRF (Reciprocal Rank Fusion):** Utilizado para fundir os dois rankings no banco de dados. Isso garante que um produto que apareceu bem nas duas buscas (tanto textual quanto semântica) fique no topo, aumentando a precisão.

### 4. Estratégia de Prompt (System Prompt)

O prompt foi desenhado com três pilares:

- **Persona:** Tom de voz amigável, prestativo e informal (como um músico conversando com outro).
- **Guardrails (Limites):** Instruções claras para nunca inventar informações (alucinação). O agente é forçado a usar as ferramentas para responder sobre preços ou regras.
- **Escopo:** O agente sabe recusar educadamente perguntas fora do escopo (ex: acessórios) e redirecionar o cliente.

### 5. Consulta SQL Dinâmica com Segurança

Para responder perguntas como "Qual o status do pedido 5?", o LLM precisa gerar SQL. Para evitar riscos de _SQL Injection_ ou comandos destrutivos, criamos uma função no Postgres (`executar_select_seguro`). Ela valida se a query começa com `SELECT` e bloqueia palavras como `DROP`, `DELETE` e `UPDATE` antes de executar via RPC.

---

## ⚠️ Limitações Conhecidas e Melhorias Futuras

O projeto foi construído para ser um MVP robusto, mas existem pontos claros de melhoria:

1. **Chunking de Políticas:** Atualmente, o PDF de políticas é "achatado" em texto pelo `pypdf` e dividido em chunks de 600 caracteres. Tabelas (como as de horários e formas de pagamento) perdem a formatação visual.
   - **O que faria com mais tempo:** Usaria uma biblioteca como `Unstructured` ou `PyMuPDF` com estratégia de extração de tabelas (`hi_res`), transformando as tabelas em JSON estruturado ou Markdown antes de gerar os embeddings.
2. **Edge Functions vs. RPC Direto:** Devido a um bug de infraestrutura no deploy da Edge Function de produtos, a busca de produtos foi movida para o SDK do Python via RPC direto no banco.
   - **O que faria com mais tempo:** Isolaria 100% da lógica de banco em Edge Functions (Deno/TypeScript) para que o frontend (Streamlit) ou um futuro app mobile não precisasse de uma chave secreta para acessar o banco.
3. **Memória da Conversa:** A memória é volátil (`st.session_state`). Se o usuário fechar a aba ou o app reiniciar, o histórico se perde.
   - **O que faria com mais tempo:** Implementaria persistência de sessão (utilizando Redis ou a própria tabela do Supabase) com um ID de sessão por usuário.
4. **Avaliação de RAG (RAGAS):** Não foi implementado um pipeline formal de avaliação da qualidade das respostas.
   - **O que faria com mais tempo:** Usaria o framework RAGAS para calcular métricas como _Faithfulness_ (fidelidade ao contexto) e _Answer Relevance_ (relevância da resposta).

---

## 🤖 Uso de Assistentes de Código (AI Workflow)

Em conformidade com o desafio, declaro que utilizei o assistente de IA **DeepSeek** (via chat) como um "par de programação" (pair programming). A ferramenta foi explorada de forma ativa e estratégica, não apenas para gerar código, mas para debater arquitetura:

- **Aceleração de Boilerplate:** Geração rápida do DDL (Data Definition Language) do banco (criação de tabelas, chaves estrangeiras e índices HNSW para o pgvector) e scripts de ETL em massa.
- **Debate de Arquitetura:** Discussão sobre os trade-offs entre usar Edge Functions vs. RPC direto, e a implementação do algoritmo RRF para busca híbrida.
- **Debugging Complexo:** A IA foi fundamental para diagnosticar problemas de infraestrutura, como erros de conexão IPv6 com o Pooler do Supabase e a tipagem estrita do Postgres (erro `numeric` vs `float8` na função de busca).
- **Refatoração:** Ajuda na migração da sintaxe antiga do LangChain (`AgentExecutor`) para a nova API (`create_agent`), mantendo o código limpo e modular.

---

_Desenvolvido para o Desafio Técnico - AI Engineer (Artefact)._
