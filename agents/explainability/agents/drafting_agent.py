from agents.explainability.utils.dummy_llm import fake_llm_response

def run_drafting_agent(clause: str):
    return {
        "agent": "Drafting Agent",
        "result": fake_llm_response(clause, "Drafting Agent")
    }
