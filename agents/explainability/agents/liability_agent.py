from agents.explainability.utils.dummy_llm import fake_llm_response

def run_liability_agent(clause: str):
    return {
        "agent": "Liability Agent",
        "result": fake_llm_response(clause, "Liability Agent")
    }
