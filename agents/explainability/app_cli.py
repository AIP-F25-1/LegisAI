from agents.explainability.cross_consistency import run_cross_consistency

if __name__ == "__main__":
    clause = input("Enter a contract clause:\n> ")
    result = run_cross_consistency(clause)
    print("\n===== Cross-Consistency Results =====")
    print(f"Clause: {result['clause']}")
    print(f"Consistency Label: {result['consistency_label']}")
    print(f"Confidence: {result['confidence']}\n")
    print("Agent Outputs:")
    for output in result["outputs"]:
        print("-", output)
