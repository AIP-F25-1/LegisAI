from agents.explainability.utils.dummy_llm import fake_llm_response

def run_risk_agent(clause: str):
    return {
        "agent": "Risk Agent",
        "result": fake_llm_response(clause, "Risk Agent")
    }
