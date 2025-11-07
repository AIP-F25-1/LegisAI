"""
cross_consistency.py
--------------------
This module orchestrates multiple specialized agents (Compliance, Risk, Drafting, etc.)
to analyze the same legal clause and check for reasoning consistency.

It aggregates responses, calculates a dummy consistency score,
and returns explainable results to the backend API.
"""

from typing import List, Dict
import random

# --- Import all agents ---
from agents.explainability.agents.compliance_agent import run_compliance_agent
from agents.explainability.agents.risk_agent import run_risk_agent
from agents.explainability.agents.drafting_agent import run_drafting_agent
from agents.explainability.agents.precedent_agent import run_precedent_agent
from agents.explainability.agents.language_quality_agent import run_language_quality_agent
from agents.explainability.agents.ethics_agent import run_ethics_agent
from agents.explainability.agents.governance_agent import run_governance_agent
from agents.explainability.agents.jurisdiction_agent import run_jurisdiction_agent
from agents.explainability.agents.negotiation_agent import run_negotiation_agent
from agents.explainability.agents.liability_agent import run_liability_agent


# --- Dummy LLM consistency simulation ---
def _dummy_consistency_score(outputs: List[str]) -> float:
    """Simulate a random consistency score (for demo purposes)."""
    return round(random.uniform(0.75, 0.98), 2)


def _aggregate_results(agent_outputs: Dict[str, str]) -> Dict:
    """Combine agent results and compute a consistency metric."""
    score = _dummy_consistency_score(list(agent_outputs.values()))
    return {
        "summary": "Cross-consistency check completed successfully.",
        "consistency_score": score,
        "outputs": [
            {"agent": name, "output": output, "confidence": round(random.uniform(0.8, 0.95), 2)}
            for name, output in agent_outputs.items()
        ]
    }


def run_cross_consistency(clause: str) -> Dict:
    """
    Run all 10 agents on a given clause and check consistency.
    Returns a unified explainable result for visualization in HITL dashboard.
    """
    try:
        print(f"\n🔍 Running cross-consistency check for clause:\n{clause}\n")

        # --- Run all agents on the same clause ---
        agent_outputs = {
            "ComplianceAgent": run_compliance_agent(clause),
            "RiskAgent": run_risk_agent(clause),
            "DraftingAgent": run_drafting_agent(clause),
            "PrecedentAgent": run_precedent_agent(clause),
            "LanguageQualityAgent": run_language_quality_agent(clause),
            "EthicsAgent": run_ethics_agent(clause),
            "GovernanceAgent": run_governance_agent(clause),
            "JurisdictionAgent": run_jurisdiction_agent(clause),
            "NegotiationAgent": run_negotiation_agent(clause),
            "LiabilityAgent": run_liability_agent(clause)
        }

        # --- Aggregate and compute consistency ---
        result = _aggregate_results(agent_outputs)

        print(f"✅ Cross-consistency check finished. Score: {result['consistency_score']}\n")
        return result

    except Exception as e:
        print(f"❌ Error during cross-consistency execution: {e}")
        return {"error": str(e)}
