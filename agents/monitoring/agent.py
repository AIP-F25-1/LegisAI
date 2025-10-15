from crewai import Agent
from .tools import crawl_sources
from agents.compliance.tools import retrieve_rules
from agents.llm import llama_llm

MonitoringAgent = Agent(
    role="Regulatory Monitoring Analyst",
    goal=("Crawl open regulation sources, summarize NEW or CHANGED requirements, and suggest clause updates."),
    backstory=("You track regulatory changes and speak succinctly."),
    tools=[crawl_sources, retrieve_rules],
    allow_delegation=False,
    verbose=True,
    llm=llama_llm(),
)
