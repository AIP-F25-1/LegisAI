from crewai import Agent
from agents.explainability.utils.dummy_llm import DummyLLM

def precedent_agent():
    return Agent(
        role="Precedent Agent",
        goal="Analyze the clause for precedent and legal consistency",
        backstory="A deterministic offline agent for precedent checking.",
        llm=DummyLLM(),     # ✅ use fake LLM instead of None
        verbose=False
    )
