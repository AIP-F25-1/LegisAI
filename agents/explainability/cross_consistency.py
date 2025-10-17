from agents.explainability.agents.precedent_agent import precedent_agent
from agents.explainability.agents.compliance_agent import compliance_agent
from agents.explainability.agents.drafting_agent import drafting_agent
from agents.explainability.agents.risk_agent import risk_agent
from agents.explainability.agents.language_quality_agent import language_quality_agent

def run_cross_consistency(clause: str):
    """
    Simulate CrewAI multi-agent reasoning and self-consistency check.
    DummyLLM responses are returned instead of real LLM calls.
    """
    agents = [
        ("Precedent Agent", precedent_agent()),
        ("Compliance Agent", compliance_agent()),
        ("Drafting Agent", drafting_agent()),
        ("Risk Agent", risk_agent()),
        ("Language Quality Agent", language_quality_agent())
    ]

    results = []

    # Simulate reasoning output instead of actual CrewAI task execution
    for name, agent in agents:
        try:
            # Access the DummyLLM directly instead of .run()
            llm = getattr(agent, "llm", None)
            if llm is not None:
                response = llm(f"Analyze this clause: {clause}")
            else:
                response = f"{name} → No LLM found."
            results.append(f"{name} → {response}")
        except Exception as e:
            results.append(f"{name} → ERROR: {str(e)}")

    return {
        "input_clause": clause,
        "results": results,
        "summary": "CrewAI consistency check completed."
    }
