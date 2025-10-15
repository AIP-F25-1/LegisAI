from crewai import Agent
from .tools import retrieve_rules, extract_clauses
from agents.llm import llama_llm

ComplianceAgent = Agent(
    role="Compliance Checker",
    goal=("Check contracts against domain packs (finance, healthcare, labor, GDPR/CCPA) and produce a clause-by-clause compliance JSON report with citations."),
    backstory=("You are a precise compliance analyst who writes concise, actionable findings."),
    tools=[retrieve_rules, extract_clauses],
    allow_delegation=False,
    verbose=True,
    llm=llama_llm(),
)
