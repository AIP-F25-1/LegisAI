from agents.explainability.dummy_llm import fake_llm_response

def run_language_quality_agent(clause):
    return f"Language Quality Agent → {fake_llm_response(clause)}"
