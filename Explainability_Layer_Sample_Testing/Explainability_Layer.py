
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from random import uniform, choice

print("Explainability Layer Initialized ✅\n")

# -----------------------------
# Step 1: Define clauses
# -----------------------------
clauses = [
    "Confidentiality clause",
    "Termination clause",
    "Indemnity clause",
    "Force Majeure clause",
    "Governing Law clause"
]

# -----------------------------
# Step 2: Define risk assessment function
# -----------------------------
def assess_clause_risk(clause):
    """
    Simulate clause risk scoring.
    Replace this with real AI/ML model or retrieval agent output later.
    Returns:
        risk_score (float): Risk score between 0 (low) and 1 (high)
        probability (float): Model confidence between 0 and 1
        citation (str): Relevant case citation
    """
    risk_score = round(uniform(0, 1), 2)
    probability = round(uniform(0, 1), 2)
    citations_list = [
        "Case A vs B, 2021",
        "Case X vs Y, 2019",
        "Case M vs N, 2020",
        "Case P vs Q, 2018",
        "Case R vs S, 2022"
    ]
    citation = choice(citations_list)
    return risk_score, probability, citation

# -----------------------------
# Step 3: Generate risk scores, probabilities, and citations
# -----------------------------
risk_scores = []
probabilities = []
citations = []

for clause in clauses:
    r, p, c = assess_clause_risk(clause)
    risk_scores.append(r)
    probabilities.append(p)
    citations.append(c)

# -----------------------------
# Step 4: Print clause-level report
# -----------------------------
print("Clause-level Risk Assessment:\n")
for i, clause in enumerate(clauses):
    print(f"{clause}:")
    print(f"  Risk Score      : {risk_scores[i]:.2f}")
    print(f"  Probability     : {probabilities[i]:.2f}")
    print(f"  Citation        : {citations[i]}\n")

# -----------------------------
# Step 5: Visualize clause risk scores as a heatmap
# -----------------------------
plt.figure(figsize=(10, 1.5))
sns.heatmap([risk_scores],
            annot=True,
            fmt=".2f",
            cmap="Reds",
            xticklabels=clauses,
            yticklabels=["Risk Score"])
plt.title("Clause-level Risk Heatmap")
plt.show()
