from agents.explainability.dummy_llm import fake_llm_response

def run_drafting_agent(clause):
    return f"Drafting Agent → {fake_llm_response(clause)}"
