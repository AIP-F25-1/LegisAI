from crewai import Crew
from ..agents import (
    precedent_agent,
    compliance_agent,
    drafting_agent,
    risk_agent,
    language_quality_agent,
)
from ..tasks import make_tasks
from ..utils.json_utils import coerce_json
from ..utils.scoring import majority_vote, aggregate_confidence, consistency_label

def run_cross_consistency(clause: str):
    print(f"[DEBUG] Running cross-consistency for clause: {clause}")

    # 1. Build agents
    agents = [
        precedent_agent(),
        compliance_agent(),
        drafting_agent(),
        risk_agent(),
        language_quality_agent()
    ]

    # 2. Create parallel tasks
    tasks = make_tasks(clause, agents)

    # 3. Run Crew
    crew = Crew(agents=agents, tasks=tasks, verbose=False)
    raw_results = crew.run()

    # 4. Dummy simulation for non-LLM agents
    for agent in agents:
        if getattr(agent, 'llm', None) == 'dummy':
            raw_results.append({
                "verdict": "revise" if agent.name == "Risk Scoring Agent" else "approve",
                "confidence": 0.7 if agent.name == "Risk Scoring Agent" else 0.9,
                "assessment": f"Simulated dummy output for {agent.name}",
                "reasons": [f"Dummy reasoning by {agent.name}"],
                "citations": []
            })

    # Normalize output
    if isinstance(raw_results, dict) and "results" in raw_results:
        outputs = raw_results["results"]
    elif isinstance(raw_results, list):
        outputs = raw_results
    else:
        outputs = [raw_results]

    parsed = [coerce_json(str(o)) for o in outputs]
    verdicts = [p.get("verdict", "review") for p in parsed]
    confidences = [float(p.get("confidence", 0.5)) for p in parsed]

    winner, counts = majority_vote(verdicts)
    agg_conf = aggregate_confidence(confidences)
    consistency = consistency_label(verdicts)

    citations = []
    seen = set()
    for p in parsed:
        for c in p.get("citations", []):
            key = (c.get("title"), c.get("url"))
            if key not in seen:
                seen.add(key)
                citations.append(c)

    summary = {
        "clause": clause,
        "per_agent": parsed,
        "cross_consistency": {
            "winner_verdict": winner,
            "vote_counts": counts,
            "consistency": consistency,
            "confidence_avg": round(agg_conf, 3)
        },
        "citations": citations
    }
    return summary
