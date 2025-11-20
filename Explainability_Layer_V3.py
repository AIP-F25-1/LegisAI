import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import csv
from random import uniform, choice

print("Explainability Layer v3 - Risk Labels, Aggregated Features & CSV Export ✅\n")

# ----------------------------------------
# Step 1: Define clauses and features
# ----------------------------------------
clauses = [
    "Confidentiality clause",
    "Termination clause",
    "Indemnity clause",
    "Force Majeure clause",
    "Governing Law clause"
]

features = ["Clarity", "Ambiguity", "Legal Precedent", "Financial Impact", "Jurisdiction Risk"]

# ----------------------------------------
# Step 2: Simulate feature importance
# ----------------------------------------
def simulate_feature_importance():
    """
    Simulates feature importance values for explainability.
    Each feature’s importance is normalized to sum to 1.
    """
    raw_importance = np.random.rand(len(features))
    normalized = raw_importance / raw_importance.sum()
    return dict(zip(features, np.round(normalized, 3)))

# ----------------------------------------
# Step 3: Clause-level risk scoring (refined)
# ----------------------------------------
def assess_clause_risk(clause: str):
    """
    Returns risk score, probability, citation and feature importance.
    """
    risk_score = round(uniform(0, 1), 2)
    probability = round(uniform(0.6, 1), 2)  # assume model is usually confident
    citation = choice([
        "Case A vs B, 2021",
        "Case X vs Y, 2019",
        "Case M vs N, 2020",
        "Case P vs Q, 2018",
        "Case R vs S, 2022"
    ])
    importance = simulate_feature_importance()
    return risk_score, probability, citation, importance

# ----------------------------------------
# Step 4: Risk label helper
# ----------------------------------------
def classify_risk(risk_score: float) -> str:
    """
    Convert continuous risk score into discrete label.
    """
    if risk_score < 0.33:
        return "Low"
    elif risk_score < 0.66:
        return "Medium"
    else:
        return "High"

# ----------------------------------------
# Step 5: Generate clause-level insights
# ----------------------------------------
results = {}
for clause in clauses:
    r, p, c, imp = assess_clause_risk(clause)
    label = classify_risk(r)
    results[clause] = {
        "Risk Score": r,
        "Risk Label": label,
        "Probability": p,
        "Citation": c,
        "Feature Importance": imp
    }

# ----------------------------------------
# Step 6: Print detailed explainability summary
# ----------------------------------------
print("Clause-level Explainability Summary\n")
for clause, details in results.items():
    print(f"🔹 {clause}")
    print(f"   Risk Score      : {details['Risk Score']:.2f}")
    print(f"   Risk Label      : {details['Risk Label']}")
    print(f"   Probability     : {details['Probability']:.2f}")
    print(f"   Citation        : {details['Citation']}")
    print("   Feature Importance:")
    for f, val in details["Feature Importance"].items():
        print(f"     {f:<20}: {val}")
    print("-" * 60)

# ----------------------------------------
# Step 7: Overall contract risk & aggregated features
# ----------------------------------------
overall_risk = np.mean([v["Risk Score"] for v in results.values()])
print(f"\n📊 Overall Contract Risk Score: {overall_risk:.2f}\n")

# Aggregate feature importance across all clauses
aggregated_feature_importance = {f: 0.0 for f in features}
for clause, details in results.items():
    for f, val in details["Feature Importance"].items():
        aggregated_feature_importance[f] += val

# Normalize aggregated feature importance
total = sum(aggregated_feature_importance.values())
aggregated_feature_importance = {
    f: round(val / total, 3) for f, val in aggregated_feature_importance.items()
}

print("Aggregated Feature Importance Across All Clauses:")
for f, val in aggregated_feature_importance.items():
    print(f"  {f:<20}: {val}")
print()

# ----------------------------------------
# Step 8: Export report to CSV
# ----------------------------------------
csv_filename = "clause_explainability_report_v3.csv"
fieldnames = ["Clause", "Risk Score", "Risk Label", "Probability", "Citation"] + features

with open(csv_filename, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for clause, details in results.items():
        row = {
            "Clause": clause,
            "Risk Score": details["Risk Score"],
            "Risk Label": details["Risk Label"],
            "Probability": details["Probability"],
            "Citation": details["Citation"],
        }
        # add feature importance columns
        for feat in features:
            row[feat] = details["Feature Importance"][feat]
        writer.writerow(row)

print(f"✅ CSV report exported: {csv_filename}\n")

# ----------------------------------------
# Step 9: Visualize aggregated feature importance (bar plot)
# ----------------------------------------
plt.figure(figsize=(8, 4))
sns.barplot(
    x=list(aggregated_feature_importance.keys()),
    y=list(aggregated_feature_importance.values())
)
plt.title("Aggregated Feature Importance Across Clauses")
plt.ylabel("Normalized Importance")
plt.xlabel("Feature")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.show()
