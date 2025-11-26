from agents.explainability.utils.dummy_llm import fake_llm_response

def run_language_quality_agent(clause: str):
    return {
        "agent": "Language Quality Agent",
        "result": fake_llm_response(clause, "Language Quality Agent")
    }
