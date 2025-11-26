def fake_llm_response(prompt: str) -> str:
    """
    Simple dummy LLM response generator.
    This prevents crashes when agents call LLM.
    """

    if not prompt:
        return "No input provided."

    # A simple rule-based fake LLM
    if "risk" in prompt.lower():
        return "Potential risk identified based on the contract clause."
    if "precedent" in prompt.lower():
        return "Relevant legal precedent may apply to similar clauses."
    if "quality" in prompt.lower():
        return "Clause quality appears acceptable with minor improvements."
    if "liability" in prompt.lower():
        return "Liability implications need clarification."

    return f"Processed: {prompt[:60]}..."