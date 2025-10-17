# agents/explainability/agents/drafting_agent.py

from crewai import Agent
from agents.explainability.utils.dummy_llm import DummyLLM

def drafting_agent():
    return Agent(
        role="Drafting Agent",
        goal="Evaluate clarity and structure of the clause.",
        backstory="Checks if the clause is grammatically and logically sound.",
        llm=DummyLLM(),
        verbose=False
    )
