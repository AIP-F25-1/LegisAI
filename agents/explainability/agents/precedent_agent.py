from agents.explainability.utils.dummy_llm import fake_llm_response

def run_precedent_agent(clause: str):
    return {
        "agent": "Precedent Agent",
        "result": fake_llm_response(clause, "Precedent Agent")
    }
