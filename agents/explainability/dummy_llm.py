import random

def fake_llm_response(prompt: str):
    responses = [
        "Clause aligns with precedent cases.",
        "Clause complies with general policies.",
        "Suggested rewrite improves clarity.",
        "Potential risk identified under confidentiality terms.",
        "Language appears consistent and legally valid.",
        "No ethical conflict found in this clause.",
        "Governance framework supports clause.",
        "Liability terms are clearly defined.",
        "Jurisdiction scope is appropriately stated.",
        "Negotiation-friendly phrasing detected."
    ]
    return random.choice(responses)
