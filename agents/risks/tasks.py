from crewai import Task

def risk_task(contract_text: str, p_default: float = 0.05, lgd: float = 0.6):
    return Task(
        description=(
            f"1) Use extract_clauses to segment.\n"
            f"2) For each clause, call score_unenforceability and justify briefly.\n"
            f"3) Run simulate_default({p_default}, {lgd}, n=5000).\n"
            "Return STRICT JSON only:\n"
            "{ \"clauses\": [ {\"id\": int, \"prob\": float, \"text\": str, \"reason\": str} ], "
            "\"mc\": {\"mean\": float, \"std\": float, \"p95\": float, \"min\": float} }"
        ),
        expected_output="Valid JSON with 'clauses' and 'mc'.",
        agent=None
    )
