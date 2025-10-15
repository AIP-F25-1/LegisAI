import numpy as np

def simulate_default(prob_default: float, loss_given_default: float, n: int = 5000):
    draws = np.random.rand(n) < prob_default
    pnl = -loss_given_default * draws.astype(float)
    return dict(mean=float(pnl.mean()),
                std=float(pnl.std()),
                p95=float(np.percentile(pnl,95)),
                min=float(pnl.min()))
