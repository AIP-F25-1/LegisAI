from agents.explainability.cross_consistency import run_cross_consistency

if __name__ == "__main__":
    print("Enter a contract clause to analyze:")
    clause = input("> ")

    results = run_cross_consistency(clause)

    print("\n===== Cross-Consistency Results =====")
    print(f"Clause: {results['clause']}")
    print(f"Consistency Label: {results['consistency_label']}")
    print(f"Confidence: {results['confidence']}")

    print("\nAgent Outputs:\n")
    for output in results['outputs']:
        print(output)

