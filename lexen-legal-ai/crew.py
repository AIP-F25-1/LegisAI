#!/usr/bin/env python

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from typing import List

@CrewBase
class LexenCrew():
    """Lexen legal AI crew for legal document analysis and research"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self) -> None:
        # Configure Ollama LLM
        self.ollama_llm = LLM(
            model="ollama/llama3",
            base_url="http://localhost:11434"
        )

    @agent
    def legal_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['legal_researcher'],
            llm=self.ollama_llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def legal_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['legal_analyst'], 
            llm=self.ollama_llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def privacy_expert(self) -> Agent:
        return Agent(
            config=self.agents_config['privacy_expert'],
            llm=self.ollama_llm,
            verbose=True,
            allow_delegation=False
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
            agent=self.legal_researcher()
        )

    @task
    def analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['analysis_task'],
            agent=self.legal_analyst(),
            context=[self.research_task()]
        )

    @task
    def summary_task(self) -> Task:
        return Task(
            config=self.tasks_config['summary_task'],
            agent=self.privacy_expert(),
            context=[self.analysis_task()]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Lexen legal crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
