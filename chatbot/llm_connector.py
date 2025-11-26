from agents.explainability.dummy_llm import run_dummy_agent

def call_llm(prompt: str) -> str:
    response = run_dummy_agent(prompt)
    return response
