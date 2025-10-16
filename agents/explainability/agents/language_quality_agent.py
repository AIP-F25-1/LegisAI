from crewai import Agent

def language_quality_agent():
    return Agent(
        role="Language Quality Agent",
        goal="Check readability, tone, and clarity of the clause.",
        backstory="Offline grammar and readability checker.",
        llm=None,
        verbose=False
    )
