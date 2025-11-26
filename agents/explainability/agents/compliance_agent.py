from agents.explainability.utils.dummy_llm import fake_llm_response

def run_compliance_agent(clause: str):
    return {
        "agent": "Compliance Agent",
        "result": fake_llm_response(clause, "Compliance Agent")
    }
