# agents/explainability/agents/language_quality_agent.py

from crewai import Agent
from agents.explainability.utils.dummy_llm import DummyLLM

def language_quality_agent():
    return Agent(
        role="Language Quality Agent",
        goal="Assess the linguistic and readability quality of the clause.",
        backstory="Reviews tone, fluency, and clarity.",
        llm=DummyLLM(),
        verbose=False
    )
