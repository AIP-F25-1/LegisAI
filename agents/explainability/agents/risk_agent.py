from agents.explainability.utils.dummy_llm import DummyLLM


from crewai import Agent

def risk_agent():
    return Agent(
        role="Risk Agent",
        goal="Identify possible risks or ambiguous terms in the clause.",
        backstory="Offline rule-based risk evaluator.",
        llm=None,
        verbose=False
    )
