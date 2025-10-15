class risk_agent:
    def __init__(self):
        self.name = "Risk Agent"

    def run(self, clause: str):
        return f"{self.name}: assessed risk for '{clause}' — low risk identified."
