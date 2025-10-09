from crewai import Agent
from .tools.retrieval_tools import precedent_lookup, regulation_lookup
from .config import OPENAI_MODEL

base_guidelines = """
- Output strictly in JSON
- Provide confidence 0–1
- Avoid hallucination; use evidence if available
"""

def precedent_agent():
    return Agent(
        name="Precedent Checker",
        role="Find case-law alignment",
        goal="Decide if clause is enforceable via precedents",
        backstory="Paralegal focusing on precedent analysis",
        tools=[precedent_lookup],
        llm=OPENAI_MODEL,
        verbose=False,
        instructions=base_guidelines
    )

def compliance_agent():
    return Agent(
        name="Compliance Checker",
        role="Check regulatory compatibility",
        goal="Assess if clause breaks compliance norms",
        backstory="Legal compliance specialist",
        tools=[regulation_lookup],
        llm=OPENAI_MODEL,
        verbose=False,
        instructions=base_guidelines
    )

def drafting_agent():
    return Agent(
        name="Drafting Reviewer",
        role="Check clarity and ambiguity",
        goal="Evaluate language and enforceability",
        backstory="Senior drafter ensuring clarity",
        tools=[precedent_lookup, regulation_lookup],
        llm=OPENAI_MODEL,
        verbose=False,
        instructions=base_guidelines
    )

# 🧪 Dummy Agents
def risk_agent():
    return Agent(
        name="Risk Scoring Agent",
        role="Estimate clause risk level",
        goal="Assign low/medium/high risk",
        backstory="Risk evaluator",
        llm="dummy"
    )

def language_quality_agent():
    return Agent(
        name="Language Quality Agent",
        role="Assess readability and grammar",
        goal="Flag unclear language",
        backstory="Language editor",
        llm="dummy"
    )
