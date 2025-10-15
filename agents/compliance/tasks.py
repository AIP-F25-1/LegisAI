from crewai import Task

def compliance_task(contract_text: str):
    return Task(
        description=(
            "1) Use extract_clauses to segment the contract.\n"
            "2) For each clause, call retrieve_rules with a focused query.\n"
            "3) Label each clause: COMPLIANT / WARNING / VIOLATION with 1-2 sentence rationale.\n"
            "4) Provide short citations (source names or filenames).\n\n"
            "Return STRICT JSON array (no extra text):\n"
            "[{\"clause_id\": int, \"text\": str, \"status\": \"COMPLIANT|WARNING|VIOLATION\", "
            "\"rationale\": str, \"citations\": [str,...]}]\n\n"
            f"CONTRACT:\n{contract_text[:15000]}"
        ),
        expected_output="A VALID JSON array only.",
        agent=None
    )
