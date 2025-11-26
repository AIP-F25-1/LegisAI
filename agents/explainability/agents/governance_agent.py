from agents.explainability.utils.dummy_llm import fake_llm_response

def run_governance_agent(clause: str):
    return {
        "agent": "Governance Agent",
        "result": fake_llm_response(clause, "Governance Agent")
    }
