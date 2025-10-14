"""
Dummy agents to simulate reasoning before real models are connected.
Each agent returns a short analysis string for the same clause.
"""

import random

def precedent_agent():
    class Dummy:
        def run(self, clause):
            responses = [
                f"Precedent found supporting clause: '{clause}'.",
                f"No clear precedent found for clause: '{clause}'.",
                f"Clause aligns with prior judgments: '{clause}'."
            ]
            return random.choice(responses)
    return Dummy()

def compliance_agent():
    class Dummy:
        def run(self, clause):
            responses = [
                f"Clause complies with standard legal frameworks.",
                f"Clause may raise minor compliance concerns.",
                f"Clause meets current compliance requirements."
            ]
            return random.choice(responses)
    return Dummy()

def drafting_agent():
    class Dummy:
        def run(self, clause):
            responses = [
                f"Suggested rewrite: Simplify language in '{clause}'.",
                f"Clause '{clause}' appears legally sound.",
                f"Clause '{clause}' can be refined for clarity."
            ]
            return random.choice(responses)
    return Dummy()
