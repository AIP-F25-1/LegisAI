from agents.explainability.agents.compliance_agent import run_compliance_agent
from agents.explainability.agents.drafting_agent import run_drafting_agent
from agents.explainability.agents.ethics_agent import run_ethics_agent
from agents.explainability.agents.governance_agent import run_governance_agent
from agents.explainability.agents.jurisdiction_agent import run_jurisdiction_agent
from agents.explainability.agents.language_quality_agent import run_language_quality_agent
from agents.explainability.agents.liability_agent import run_liability_agent
from agents.explainability.agents.negotiation_agent import run_negotiation_agent
from agents.explainability.agents.precedent_agent import run_precedent_agent
from agents.explainability.agents.risk_agent import run_risk_agent


def run_cross_consistency(clause: str):
    agents = [
        run_compliance_agent,
        run_drafting_agent,
        run_ethics_agent,
        run_governance_agent,
        run_jurisdiction_agent,
        run_language_quality_agent,
        run_liability_agent,
        run_negotiation_agent,
        run_precedent_agent,
        run_risk_agent,
    ]

    results = []
    for agent in agents:
        try:
            results.append(agent(clause))
        except Exception as e:
            results.append({"agent": agent.__name__, "error": str(e)})

    return {"input": clause, "results": results}
