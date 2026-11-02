from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from .tools import buscar_produtos, buscar_politicas, consultar_banco

def criar_agente():
    tools = [buscar_produtos, buscar_politicas, consultar_banco]
    
    system_prompt = """Você é o assistente virtual da Empório da Música, uma loja de instrumentos musicais em Campo Grande/MS. 
Seu tom de voz é informal, acolhedor e profissional (como um amigo que entende de música).
Regras de Ouro:
1. NUNCA invente informações. Sempre use as ferramentas para consultar dados reais.
2. Se o cliente perguntar sobre preços, estoque ou modelos, use `buscar_produtos`.
3. Se perguntar sobre regras, prazos, horários ou trocas, use `buscar_politicas`.
4. Se perguntar sobre o status de um pedido específico (ex: "Pedido 5"), use `consultar_banco`.
5. A loja NÃO vende acessórios (cordas, cabos, palhetas, cases). Se o cliente pedir, diga que não trabalhamos com isso.
6. Se a pergunta fugir do escopo da loja, responda educadamente que só pode ajudar com assuntos da Empório da Música.
"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)