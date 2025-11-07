from agents.explainability.utils.dummy_llm import fake_llm_response

def run_liability_agent(clause: str):
    """
    Simulates an agent that detects possible liability risks in the clause.
    Flags terms that could expose the party to excessive legal responsibility.
    """
    return fake_llm_response(f"Liability analysis of: {clause}")
