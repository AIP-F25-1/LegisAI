# agents/explainability/agents/compliance_agent.py

from crewai import Agent
from agents.explainability.utils.dummy_llm import DummyLLM

def compliance_agent():
    return Agent(
        role="Compliance Agent",
        goal="Ensure the clause aligns with legal and regulatory compliance.",
        backstory="Evaluates laws, jurisdiction, and compliance implications.",
        llm=DummyLLM(),
        verbose=False
    )
