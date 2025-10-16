"""
Main CrewAI crew definition for LexenAI
Multi-agent legal intelligence system
"""

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from typing import List, Dict, Any
import structlog

from research_agents import create_research_agents
from drafting_agents import create_drafting_agents
from compliance_agents import create_compliance_agents
from explainability_agents import create_explainability_agents
from multimodal_agents import create_multimodal_agents
from config.settings import settings

logger = structlog.get_logger(__name__)

@CrewBase
class LexenAICrew:
    """
    LexenAI Legal Intelligence Crew
    Orchestrates 15+ specialized AI agents for comprehensive legal workflows
    """

    agents_config = '../config/agents.yaml'
    tasks_config = '../config/tasks.yaml'

    def __init__(self) -> None:
        # Configure Ollama LLM
        self.ollama_llm = LLM(
            model=settings.LITELLM_MODEL,
            base_url=settings.LITELLM_API_BASE
        )
        logger.info("🤖 Initialized LexenAI Crew with Ollama LLM")

    # Research & Retrieval Intelligence Agents
    @agent
    def semantic_retrieval_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['semantic_retrieval_agent'],
            llm=self.ollama_llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def summarization_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['summarization_agent'],
            llm=self.ollama_llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def precedent_reasoning_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['precedent_reasoning_agent'],
            llm=self.ollama_llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def knowledge_graph_builder(self) -> Agent:
        return Agent(
            config=self.agents_config['knowledge_graph_builder'],
            llm=self.ollama_llm,
            verbose=True,
            allow_delegation=False
        )

    # Drafting & Contract Intelligence Agents
    @agent
    def contract_drafting_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['contract_drafting_agent'],
            llm=self.ollama_llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def clause_analysis_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['clause_analysis_agent'],
            llm=self.ollama_llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def redlining_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['redlining_agent'],
            llm=self.ollama_llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def clause_generation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['clause_generation_agent'],
            llm=self.ollama_llm,
            verbose=True,
            allow_delegation=False
        )

    # Compliance & Risk Intelligence Agents
    @agent
    def compliance_checker_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['compliance_checker_agent'],
            llm=self.ollama_llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def regulatory_monitoring_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['regulatory_monitoring_agent'],
            llm=self.ollama_llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def risk_assessment_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['risk_assessment_agent'],
            llm=self.ollama_llm,
            verbose=True,
            allow_delegation=False
        )

    # Explainability & HITL Agents
    @agent
    def explainability_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['explainability_agent'],
            llm=self.ollama_llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def reasoning_consistency_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['reasoning_consistency_agent'],
            llm=self.ollama_llm,
            verbose=True,
            allow_delegation=False
        )

    # Multi-Modal Legal Intelligence Agents
    @agent
    def document_ocr_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['document_ocr_agent'],
            llm=self.ollama_llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def timeline_builder_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['timeline_builder_agent'],
            llm=self.ollama_llm,
            verbose=True,
            allow_delegation=False
        )

    # Task Definitions
    @task
    def legal_research_task(self) -> Task:
        return Task(
            config=self.tasks_config['legal_research_task'],
            agent=self.semantic_retrieval_agent()
        )

    @task
    def document_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['document_analysis_task'],
            agent=self.summarization_agent(),
            context=[self.legal_research_task()]
        )

    @task
    def contract_drafting_task(self) -> Task:
        return Task(
            config=self.tasks_config['contract_drafting_task'],
            agent=self.contract_drafting_agent(),
            context=[self.document_analysis_task()]
        )

    @task
    def compliance_check_task(self) -> Task:
        return Task(
            config=self.tasks_config['compliance_check_task'],
            agent=self.compliance_checker_agent(),
            context=[self.contract_drafting_task()]
        )

    @task
    def risk_assessment_task(self) -> Task:
        return Task(
            config=self.tasks_config['risk_assessment_task'],
            agent=self.risk_assessment_agent(),
            context=[self.compliance_check_task()]
        )

    @task
    def explainability_task(self) -> Task:
        return Task(
            config=self.tasks_config['explainability_task'],
            agent=self.explainability_agent(),
            context=[self.risk_assessment_task()],
            output_file="output/legal_analysis_report.md"
        )

    @crew
    def crew(self) -> Crew:
        """Creates the LexenAI legal intelligence crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,
            planning=True
        )

    async def execute_workflow(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the complete legal AI workflow"""
        try:
            logger.info("🚀 Starting LexenAI workflow", inputs=inputs)

            # Execute the crew
            result = self.crew().kickoff(inputs=inputs)

            logger.info("✅ LexenAI workflow completed successfully")
            return {
                "success": True,
                "result": result,
                "workflow": "complete_legal_analysis"
            }

        except Exception as e:
            logger.error("❌ LexenAI workflow failed", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "workflow": "complete_legal_analysis"
            }
