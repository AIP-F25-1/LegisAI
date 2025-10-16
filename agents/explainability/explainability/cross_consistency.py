from crewai import Crew
from agents.explainability.agents.precedent_agent import precedent_agent
from agents.explainability.agents.compliance_agent import compliance_agent
from agents.explainability.agents.drafting_agent import drafting_agent
from agents.explainability.agents.risk_agent import risk_agent
from agents.explainability.agents.language_quality_agent import language_quality_agent

def run_cross_consistency(clause: str):
    """
    Run CrewAI locally without any external OpenAI calls.
    """
    agents = [
        precedent_agent(),
        compliance_agent(),
        drafting_agent(),
        risk_agent(),
        language_quality_agent()
    ]

    tasks = [f"Offline analysis of clause: {clause}" for _ in agents]
    crew = Crew(agents=agents, tasks=tasks, verbose=False)

    raw_results = crew.run()
    if isinstance(raw_results, dict) and "results" in raw_results:
        outputs = raw_results["results"]
    elif isinstance(raw_results, list):
        outputs = raw_results
    else:
        outputs = [str(raw_results)]

    return {a.role: o for a, o in zip(agents, outputs)}
