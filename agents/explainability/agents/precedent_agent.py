from agents.explainability.utils.dummy_llm import fake_llm_response

def run_precedent_agent(clause: str):
    return fake_llm_response(f"Precedent analysis of: {clause}")
