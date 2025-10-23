from typing import Dict, List
from .dummy_llm import (
    precedent_opinion, compliance_opinion, drafting_suggestion,
    risk_analysis, language_quality
)
from .utils.json_utils import make_response

# ---- local dummy run ----
def run_agents_locally(clause: str) -> Dict[str, str]:
    """Simulate 5 agents running independently on the same clause."""
    return {
        "precedent": precedent_opinion(clause),
        "compliance": compliance_opinion(clause),
        "drafting": drafting_suggestion(clause),
        "risk": risk_analysis(clause),
        "language_quality": language_quality(clause),
    }

# ---- consistency logic ----
NEG = {"violate", "conflict", "unenforceable", "risk", "ambiguous", "missing", "unclear"}
POS = {"ok", "compliant", "aligns", "acceptable"}

def detect_conflicts(outputs: Dict[str, str]) -> List[str]:
    notes: List[str] = []
    has_pos = any(any(w in o.lower() for w in POS) for o in outputs.values())
    has_neg = any(any(w in o.lower() for w in NEG) for o in outputs.values())
    if has_pos and has_neg:
        notes.append("Some agents flag legal issues while others mark the clause compliant.")
    if "consumer" in outputs.get("compliance", "").lower():
        notes.append("Compliance flagged consumer-cap conflict.")
    if "Language Quality Agent" in outputs.get("language_quality", "") and "unenforceable" in " ".join(outputs.values()).lower():
        notes.append("Language quality may impact enforceability.")
    return notes

def harmonize(_: Dict[str, str]) -> str:
    return ("Harmonized Conclusion: keep liability cap (≥ $25 000 or 1× fees), "
            "exclude fraud / gross negligence, define 'Losses', "
            "and verify consumer law compliance. Use clear language.")

# ---- public entry ----
def cross_consistency_check(clause: str) -> Dict[str, str]:
    outputs = run_agents_locally(clause)
    conflicts = detect_conflicts(outputs)
    merged = harmonize(outputs)
    return make_response(clause, outputs, conflicts, merged)
