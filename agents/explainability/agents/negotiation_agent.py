from agents.explainability.utils.dummy_llm import fake_llm_response

def run_negotiation_agent(clause: str):
    """
    Simulates an agent that reviews how the clause might impact negotiations.
    Identifies overly rigid terms, leverage points, and potential deal blockers.
    """
    return fake_llm_response(f"Negotiation review of: {clause}")
