from agents.explainability.explainability.cross_consistency import run_cross_consistency

if __name__ == "__main__":
    clause = input("Enter clause: ")
    result = run_cross_consistency(clause)
    for k, v in result.items():
        print(f"{k}: {v}")
