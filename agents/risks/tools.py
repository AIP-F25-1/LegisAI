from crewai_tools import tool
from .monte_carlo import simulate_default
from .scoring import heuristic_unenforceability_prob

@tool("simulate_default", return_direct=False)
def t_simulate_default(prob_default: float, loss_given_default: float, n: int = 5000) -> str:
    """Monte Carlo default scenario; returns stats as JSON-like string."""
    res = simulate_default(prob_default, loss_given_default, n)
    return str(res)

@tool("score_unenforceability", return_direct=False)
def t_score_unenforceability(clause: str) -> str:
    """Baseline unenforceability probability [0..1]."""
    return f"{heuristic_unenforceability_prob(clause):.2f}"
