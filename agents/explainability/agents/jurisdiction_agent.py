from agents.explainability.utils.dummy_llm import fake_llm_response

def run_jurisdiction_agent(clause: str):
    return {
        "agent": "Jurisdiction Agent",
        "result": fake_llm_response(clause, "Jurisdiction Agent")
    }
