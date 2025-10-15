"""
Explainability & Self-Consistency Runner
Simulated multi-agent orchestration using dummy agents.
"""

import sys
import os
import random

# ✅ Ensure Python can find dummy_agents inside this folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dummy_agents import precedent_agent, compliance_agent, drafting_agent

# ---------- CONSISTENCY LOGIC ----------
def majority_vote(outputs):
    """Return CONSISTENT if most outputs are similar."""
    normalized = [o.lower() for o in outputs]
    common = max(set(normalized), key=normalized.count)
    agreement_ratio = normalized.count(common) / len(outputs)
    return "CONSISTENT" if agreement_ratio >= 0.6 else "INCONSISTENT"

def aggregate_confidence(outputs):
    """Generate fake confidence between 0.5 and 1.0."""
    return round(random.uniform(0.5, 1.0), 2)

# ---------- MAIN ORCHESTRATOR ----------
def run_cross_consistency(clause: str):
    """Simulates multi-agent reasoning using dummy agents."""
    agents = [precedent_agent(), compliance_agent(), drafting_agent()]

    outputs = []
    for agent in agents:
        result = agent.run(clause)
        outputs.append(result)

    label = majority_vote(outputs)
    confidence = aggregate_confidence(outputs)

    return {
        "clause": clause,
        "outputs": outputs,
        "consistency_label": label,
        "confidence": confidence
    }

# ---------- CLI ENTRY ----------
if __name__ == "__main__":
    clause = input("Enter a contract clause to analyze:\n> ")
    result = run_cross_consistency(clause)

    print("\n===== Cross-Consistency Results =====")
    print(f"Clause: {result['clause']}")
    print(f"Consistency Label: {result['consistency_label']}")
    print(f"Confidence: {result['confidence']}")
    print("\nAgent Outputs:")
    for i, out in enumerate(result["outputs"], 1):
        print(f"\nAgent {i}: {out}")
