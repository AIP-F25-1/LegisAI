def compute_confidence(results: list):
    return round(0.75 + (len(results) / 100), 2)
