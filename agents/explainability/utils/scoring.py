import random

def calculate_consistency(outputs):
    unique_responses = len(set(outputs))
    if unique_responses == 1:
        return "CONSISTENT", round(random.uniform(0.8, 1.0), 2)
    elif unique_responses <= 3:
        return "PARTIALLY CONSISTENT", round(random.uniform(0.6, 0.8), 2)
    else:
        return "INCONSISTENT", round(random.uniform(0.4, 0.6), 2)
