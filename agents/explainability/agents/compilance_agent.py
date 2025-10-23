from agents.explainability.dummy_llm import fake_llm_response

def run_compliance_agent(clause):
    return f"Compliance Agent → {fake_llm_response(clause)}"
