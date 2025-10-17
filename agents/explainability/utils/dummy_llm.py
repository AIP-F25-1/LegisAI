class DummyLLM:
    """
    A fake lightweight LLM used for offline CrewAI testing.
    It now includes a .bind() method for CrewAI >= 0.51 compatibility.
    """

    def __init__(self):
        pass

    def bind(self, **kwargs):
        """CrewAI expects LLMs to support .bind(stop=...)"""
        return self  # just return self to keep chain continuity

    def __call__(self, prompt):
        """Simulate a text-generation response."""
        return f"Simulated response for: '{prompt[:60]}...'"

    def run(self, prompt):
        """Alias for backwards compatibility."""
        return self.__call__(prompt)
