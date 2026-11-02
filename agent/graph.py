from langchain_openai import ChatOpenAI
from langchain.agents import create_agent # <-- Importação nova
from .tools import buscar_produtos, buscar_politicas, consultar_banco

def criar_agente():
    tools = [buscar_produtos, buscar_politicas, consultar_banco]

    system_prompt = """Você é o assistente virtual da Empório da Música..."""
    # (Mantenha o seu system_prompt exatamente como estava)

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

    # O create_agent já monta o prompt e o executor internamente
    agente = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt
    )
    
    return agente