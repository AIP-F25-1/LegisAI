from crewai import Agent

def drafting_agent():
    return Agent(
        role="Drafting Agent",
        goal="Evaluate clarity and drafting quality of the clause.",
        backstory="Checks if the clause is grammatically and structurally correct.",
        llm=None,
        verbose=False
    )
