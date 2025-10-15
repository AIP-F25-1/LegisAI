from crewai import Agent
from .tools import t_simulate_default, t_score_unenforceability
from agents.compliance.tools import extract_clauses
from agents.llm import llama_llm

RiskAgent = Agent(
    role="Contract Risk Assessor",
    goal=("Estimate clause-level unenforceability probabilities and run Monte Carlo what-if scenarios."),
    backstory=("Quantitative, cautious, explains assumptions briefly."),
    tools=[extract_clauses, t_score_unenforceability, t_simulate_default],
    allow_delegation=False,
    verbose=True,
    llm=llama_llm(),
)
