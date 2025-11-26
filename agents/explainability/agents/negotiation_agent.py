from agents.explainability.utils.dummy_llm import fake_llm_response

def run_negotiation_agent(clause: str):
    return {
        "agent": "Negotiation Agent",
        "result": fake_llm_response(clause, "Negotiation Agent")
    }
