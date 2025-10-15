def heuristic_unenforceability_prob(clause: str) -> float:
    risk = 0.0
    if len(clause) < 100: risk += 0.2
    kws = ["sole discretion","waive","indemnify","limitation of liability", "force majeure","arbitration","non-compete","liquidated damages"]
    for k in kws:
        if k in clause.lower(): risk += 0.15
    return min(risk, 1.0)
