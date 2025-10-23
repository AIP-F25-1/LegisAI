from agents.explainability.dummy_llm import fake_llm_response

def run_precedent_agent(clause):
    return f"Precedent Agent → {fake_llm_response(clause)}"
