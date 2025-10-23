from agents.explainability.dummy_llm import fake_llm_response

def run_risk_agent(clause):
    return f"Risk Agent → {fake_llm_response(clause)}"
