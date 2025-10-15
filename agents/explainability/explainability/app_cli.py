from src.pipelines.review_clause import run_cross_consistency

if __name__ == "__main__":
    clause = (
        "The employee shall not compete with the employer in any capacity "
        "for two (2) years after termination within North America."
    )

    print("\n=== CROSS-CONSISTENCY SUMMARY ===\n")
    result = run_cross_consistency(clause)

    print("Clause:", result["clause"])
    cc = result["cross_consistency"]
    print(f"\nWinner Verdict: {cc['winner_verdict']} | Consistency: {cc['consistency']} | Avg Confidence: {cc['confidence_avg']}")
    print("Vote Counts:", cc["vote_counts"])

    print("\n--- Per-Agent Outputs (JSON) ---")
    for i, pa in enumerate(result["per_agent"], 1):
        print(f"\nAgent {i} ({pa.get('verdict','N/A')}):", pa)

    print("\n--- Citations ---")
    if not result["citations"]:
        print("No citations found.")
    else:
        for c in result["citations"]:
            print(f"- {c.get('title')} [{c.get('jurisdiction')}] -> {c.get('url')}")
