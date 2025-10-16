from langchain_core.runnables import Runnable

class DummyLLM(Runnable):
    """A fake LLM compatible with CrewAI (acts like a LangChain Runnable)."""

    def invoke(self, input_text, **kwargs):
        """Simulate text generation."""
        return f"Offline CrewAI dummy result for: {input_text}"

    def bind(self, **kwargs):
        """Return self — required by CrewAI when chaining runnables."""
        return self
