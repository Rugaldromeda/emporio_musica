# 🎸 Empório da Música - AI Customer Service Agent

This project is a virtual customer service agent built in Python with Streamlit, using LangChain and OpenAI for tool routing (Tool Calling), and Supabase (PostgreSQL + pgvector) as the database.

## 🌐 Live Application

You can try the agent directly in your browser, no installation needed:
👉 **[Access the Empório da Música Agent](https://emporiomusica.streamlit.app)**

## 🚀 Running the project

### Prerequisites

- Python 3.10+
- Supabase account
- OpenAI API key

### 1. Environment setup

```bash
git clone https://github.com/seu-usuario/emporio-da-musica.git
cd emporio-da-musica
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the `creds/` folder with:

```env
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_KEY="your-secret-key-here"
OPENAI_API_KEY="your-openai-key-here"
DATABASE_URL="postgresql://..." # Only for the ETL scripts
```

### 3. Running the Agent

```bash
streamlit run app.py
```

---

## 🧠 Technical Decisions and Justifications

### 1. Framework: LangChain (v1.x) and Streamlit

- **Streamlit:** Chosen for the speed it offers in building chat interfaces. It allows prototyping a functional frontend in a few lines of code, without needing to build a complex React/Next.js app for a proof of concept.
- **LangChain:** Used for its mature **Tool Calling** abstraction. The modern version (`create_agent`) lets the LLM dynamically decide which tool to use, while keeping conversation memory and history simple to manage.

### 2. LLM: `gpt-4o-mini`

- **Justification:** It's an extremely fast model with excellent cost-benefit for customer service. It has a context window large enough for the rules and history, and its *function calling* capability is very precise for our scope.

### 3. Retrieval Architecture: Hybrid RAG

For product and policy search, we didn't rely on vector search alone. We implemented a **Hybrid RAG** directly in PostgreSQL:

- **Vector Search (`pgvector`):** Solves the vocabulary problem (e.g., a customer searches for "instrument with soft strings" and finds a "nylon-string guitar").
- **Full-Text Search (`tsvector`):** Ensures exact terms aren't lost (e.g., "PIX", "12x" installments, model names like "Takamine GD20").
- **RRF (Reciprocal Rank Fusion):** Used to merge the two rankings at the database level. This ensures a product that ranked well in both searches (textual and semantic) stays on top, increasing precision.

### 4. Prompt Strategy (System Prompt)

The prompt was designed around three pillars:

- **Persona:** A friendly, helpful, and informal tone of voice (like one musician talking to another).
- **Guardrails:** Clear instructions to never make up information (hallucination). The agent is forced to use the tools to answer questions about prices or policies.
- **Scope:** The agent politely declines out-of-scope questions (e.g., accessories) and redirects the customer.

### 5. Secure Dynamic SQL Querying

To answer questions like "What's the status of order 5?", the LLM needs to generate SQL. To avoid SQL Injection risks or destructive commands, we created a Postgres function (`executar_select_seguro`). It validates that the query starts with `SELECT` and blocks keywords such as `DROP`, `DELETE`, and `UPDATE` before executing it via RPC.

---

## ⚠️ Known Limitations and Future Improvements

The project was built as a solid MVP, but there are clear areas for improvement:

1. **PDF Chunking and Table Extraction**
   **Context:** The store's policy manual is full of tables (payment methods, hours, shipping times). The `pypdf` library used for ingestion extracts text linearly, "flattening" tables into running text. Additionally, to maintain compatibility with the LangChain ecosystem during initial processing, we configured `RecursiveCharacterTextSplitter` with 600-character chunks to ensure no table row was cut in half, preserving data integrity (even if the text looks visually fragmented).

   **Impact:** The LLM is able to interpret the running text and answer policy questions correctly (as validated in testing), but loses the visual hierarchy of the tables.

2. **Edge Functions vs. Direct RPC:** Due to an infrastructure bug in the deployment of the products Edge Function, product search was moved to the Python SDK via direct RPC to the database.
   - **What I would do with more time:** I would isolate 100% of the database logic in Edge Functions (Deno/TypeScript) so the frontend (Streamlit) or a future mobile app wouldn't need a secret key to access the database.
3. **Conversation Memory:** Memory is volatile (`st.session_state`). If the user closes the tab or the app restarts, the history is lost.
   - **What I would do with more time:** I would implement session persistence (using Redis or a Supabase table) with a per-user session ID.
4. **RAG Evaluation (RAGAS):** A formal pipeline for evaluating response quality was not implemented.
   - **What I would do with more time:** I would use the RAGAS framework to calculate metrics such as *Faithfulness* (fidelity to context) and *Answer Relevance*.
5. **Prompt Caching:** Currently, the system prompt is resent with every request. I would implement OpenAI's Prompt Caching (or use LangChain's native cache) to reduce cost and latency; the gain grows with the length of the accumulated conversation history, and since the test sessions had few exchanges, the impact in the current scenario would be small.

---

## 🤖 Use of AI Coding Assistants (AI Workflow)

In compliance with the challenge requirements, I declare that I used the AI assistant **DeepSeek** (via chat) as a "pair programmer." The tool was used actively and strategically, not just to generate code but to discuss architecture:

- **Boilerplate Acceleration:** Quick generation of the database DDL (Data Definition Language) (table creation, foreign keys, and HNSW indexes for pgvector) and bulk ETL scripts.
- **Architecture Discussion:** Discussing the trade-offs between using Edge Functions vs. direct RPC, and the implementation of the RRF algorithm for hybrid search.
- **Complex Debugging:** The AI was key to diagnosing infrastructure issues, such as IPv6 connection errors with the Supabase Pooler and strict Postgres typing (`numeric` vs `float8` error in the search function).
- **Refactoring:** Help migrating the old LangChain syntax (`AgentExecutor`) to the new API (`create_agent`), keeping the code clean and modular.

---

_Developed for the Technical Challenge - AI Engineer (Artefact)._
