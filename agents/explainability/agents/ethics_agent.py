from agents.explainability.utils.dummy_llm import fake_llm_response

def run_ethics_agent(clause: str):
    return {
        "agent": "Ethics Agent",
        "result": fake_llm_response(clause, "Ethics Agent")
    }
