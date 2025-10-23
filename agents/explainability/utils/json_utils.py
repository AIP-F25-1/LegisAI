from typing import Any, Dict, List

def make_response(clause: str, agent_outputs: Dict[str, str], conflicts: List[str], harmonized: str) -> Dict[str, Any]:
    """Return a consistent JSON payload for the API."""
    return {
        "clause": clause,
        "agents": agent_outputs,
        "consistency": {
            "conflicts": conflicts,
            "harmonized_conclusion": harmonized
        }
    }
