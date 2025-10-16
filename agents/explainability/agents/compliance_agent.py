from crewai import Agent

def compliance_agent():
    return Agent(
        role="Compliance Agent",
        goal="Ensure the clause aligns with legal compliance standards.",
        backstory="A simple offline compliance analyzer.",
        llm=None,
        verbose=False
    )
