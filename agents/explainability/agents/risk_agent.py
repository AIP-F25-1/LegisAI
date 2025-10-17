# agents/explainability/agents/risk_agent.py

from crewai import Agent
from agents.explainability.utils.dummy_llm import DummyLLM

def risk_agent():
    return Agent(
        role="Risk Agent",
        goal="Identify potential legal or operational risks in the clause.",
        backstory="Focuses on ambiguity, liability, and risk factors.",
        llm=DummyLLM(),
        verbose=False
    )
