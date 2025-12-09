"""
LangGraph Orchestrator Service
Orchestrates multiple agents using LangGraph for complex workflows with state management
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional, Annotated
try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Try to import LangGraph
try:
    from langgraph.graph import StateGraph, END
    from langgraph.graph.message import add_messages
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    StateGraph = None
    END = None
    add_messages = None
    logger.warning("⚠️ LangGraph not available. Install with: pip install langgraph langchain-core")

# Define workflow state
class WorkflowState(TypedDict):
    """State passed between workflow nodes"""
    contract_text: str
    jurisdiction: str
    risk_score: Optional[float]
    risk_level: Optional[str]
    risk_issues: List[str]
    compliance_issues: List[str]
    missing_clauses: List[str]
    generated_clauses: Dict[str, str]
    consistency_results: Dict[str, Any]
    agent_results: Dict[str, Any]
    workflow_step: str
    errors: List[str]

class LangGraphOrchestrator:
    """Orchestrates multiple agents using LangGraph"""
    
    def __init__(
        self,
        summarization_agent=None,
        precedent_reasoning_agent=None,
        clause_analyzer=None,
        clause_generation_agent=None,
        redlining_agent=None,
        regulatory_monitoring_agent=None,
        monte_carlo_agent=None,
        ollama_client=None,
        ollama_model: str = "llama3.1:8b"
    ):
        """
        Initialize LangGraph orchestrator
        
        Args:
            summarization_agent: SummarizationAgent instance
            precedent_reasoning_agent: PrecedentReasoningAgent instance
            clause_analyzer: ClauseAnalyzer instance
            clause_generation_agent: ClauseGenerationAgent instance
            redlining_agent: RedliningComparisonAgent instance
            regulatory_monitoring_agent: RegulatoryMonitoringAgent instance
            monte_carlo_agent: MonteCarloRiskAgent instance
            ollama_client: Ollama client for AI tasks
            ollama_model: Model name to use
        """
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("LangGraph not available. Install with: pip install langgraph langchain-core")
        
        # Store references to existing agents
        self.summarization_agent = summarization_agent
        self.precedent_reasoning_agent = precedent_reasoning_agent
        self.clause_analyzer = clause_analyzer
        self.clause_generation_agent = clause_generation_agent
        self.redlining_agent = redlining_agent
        self.regulatory_monitoring_agent = regulatory_monitoring_agent
        self.monte_carlo_agent = monte_carlo_agent
        self.ollama_client = ollama_client
        self.ollama_model = ollama_model
        
        # Build workflow graphs
        self.comprehensive_workflow = self._build_comprehensive_workflow()
        self.research_draft_workflow = self._build_research_draft_workflow()
        self.consistency_check_workflow = self._build_consistency_check_workflow()
    
    def _build_comprehensive_workflow(self) -> Optional[StateGraph]:
        """Build comprehensive analysis workflow: Risk → Compliance → Clauses → Consistency"""
        if not LANGGRAPH_AVAILABLE:
            return None
        
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("risk_analysis", self._risk_analysis_node)
        workflow.add_node("compliance_check", self._compliance_check_node)
        workflow.add_node("missing_clauses", self._missing_clauses_node)
        workflow.add_node("consistency_check", self._consistency_check_node)
        
        # Set entry point
        workflow.set_entry_point("risk_analysis")
        
        # Add conditional edges based on risk level
        workflow.add_conditional_edges(
            "risk_analysis",
            self._route_by_risk_level,
            {
                "high": "compliance_check",
                "medium": "compliance_check",
                "low": "missing_clauses",
                "critical": "compliance_check"
            }
        )
        
        # Continue workflow
        workflow.add_edge("compliance_check", "missing_clauses")
        workflow.add_edge("missing_clauses", "consistency_check")
        workflow.add_edge("consistency_check", END)
        
        return workflow.compile()
    
    def _build_research_draft_workflow(self) -> Optional[StateGraph]:
        """Build research → draft → review workflow"""
        if not LANGGRAPH_AVAILABLE:
            return None
        
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("research", self._research_node)
        workflow.add_node("draft", self._draft_node)
        workflow.add_node("review", self._review_node)
        
        # Set entry point
        workflow.set_entry_point("research")
        
        # Sequential flow
        workflow.add_edge("research", "draft")
        workflow.add_edge("draft", "review")
        workflow.add_edge("review", END)
        
        return workflow.compile()
    
    def _build_consistency_check_workflow(self) -> Optional[StateGraph]:
        """Build cross-consistency check workflow"""
        if not LANGGRAPH_AVAILABLE:
            return None
        
        workflow = StateGraph(WorkflowState)
        
        # Add nodes for different agents analyzing the same clause
        workflow.add_node("risk_analysis", self._risk_analysis_node)
        workflow.add_node("compliance_check", self._compliance_check_node)
        workflow.add_node("clause_analysis", self._clause_analysis_node)
        workflow.add_node("consistency_analysis", self._consistency_analysis_node)
        
        # Set entry point
        workflow.set_entry_point("risk_analysis")
        
        # Run all agents in parallel (using conditional to start all)
        workflow.add_edge("risk_analysis", "compliance_check")
        workflow.add_edge("compliance_check", "clause_analysis")
        workflow.add_edge("clause_analysis", "consistency_analysis")
        workflow.add_edge("consistency_analysis", END)
        
        return workflow.compile()
    
    # Node implementations
    async def _risk_analysis_node(self, state: WorkflowState) -> WorkflowState:
        """Analyze contract for risks"""
        logger.info("🔍 Risk Analysis Node")
        state["workflow_step"] = "risk_analysis"
        
        if not self.clause_analyzer:
            state["errors"].append("Clause analyzer not available")
            return state
        
        try:
            # Analyze first clause or entire contract
            clause_text = state["contract_text"][:500]  # Sample clause
            risk = self.clause_analyzer.analyze_clause(
                clause_text,
                state.get("jurisdiction", "US"),
                ""
            )
            
            state["risk_score"] = risk.risk_score
            state["risk_level"] = risk.risk_level
            state["risk_issues"] = risk.issues[:5]  # Top 5 issues
            state["agent_results"]["risk_analyzer"] = {
                "risk_level": risk.risk_level,
                "risk_score": risk.risk_score,
                "issues": risk.issues
            }
            
            logger.info(f"✅ Risk analysis complete: {risk.risk_level} ({risk.risk_score:.2f})")
        except Exception as e:
            logger.error(f"Error in risk analysis: {e}")
            state["errors"].append(f"Risk analysis error: {str(e)}")
        
        return state
    
    async def _compliance_check_node(self, state: WorkflowState) -> WorkflowState:
        """Check contract for compliance issues"""
        logger.info("📋 Compliance Check Node")
        state["workflow_step"] = "compliance_check"
        
        # Simulate compliance check (you can integrate actual compliance agent)
        try:
            # Basic compliance check logic
            compliance_issues = []
            
            # Check for common compliance issues
            contract_lower = state["contract_text"].lower()
            if "gdpr" not in contract_lower and "data protection" not in contract_lower:
                compliance_issues.append("Missing GDPR/data protection clause")
            
            if state.get("risk_level") in ["high", "critical"]:
                compliance_issues.append("High risk contract requires additional compliance review")
            
            state["compliance_issues"] = compliance_issues
            state["agent_results"]["compliance_checker"] = {
                "issues": compliance_issues,
                "jurisdiction": state.get("jurisdiction", "US")
            }
            
            logger.info(f"✅ Compliance check complete: {len(compliance_issues)} issues found")
        except Exception as e:
            logger.error(f"Error in compliance check: {e}")
            state["errors"].append(f"Compliance check error: {str(e)}")
        
        return state
    
    async def _missing_clauses_node(self, state: WorkflowState) -> WorkflowState:
        """Detect and generate missing clauses"""
        logger.info("📝 Missing Clauses Node")
        state["workflow_step"] = "missing_clauses"
        
        if not self.clause_generation_agent:
            state["errors"].append("Clause generation agent not available")
            return state
        
        try:
            # Detect missing clauses
            missing = self.clause_generation_agent.detect_missing_clauses(
                state["contract_text"]
            )
            
            state["missing_clauses"] = missing
            
            # Generate clauses for missing types
            generated = {}
            for clause_type in missing[:3]:  # Generate top 3 missing clauses
                try:
                    result = await self.clause_generation_agent.generate_clause(clause_type)
                    generated[clause_type] = result.get("generated_clause", "")
                except Exception as e:
                    logger.warning(f"Failed to generate {clause_type}: {e}")
            
            state["generated_clauses"] = generated
            state["agent_results"]["clause_generator"] = {
                "missing_clauses": missing,
                "generated": list(generated.keys())
            }
            
            logger.info(f"✅ Missing clauses analysis: {len(missing)} missing, {len(generated)} generated")
        except Exception as e:
            logger.error(f"Error in missing clauses: {e}")
            state["errors"].append(f"Missing clauses error: {str(e)}")
        
        return state
    
    async def _consistency_check_node(self, state: WorkflowState) -> WorkflowState:
        """Check consistency across agent results"""
        logger.info("🔍 Consistency Check Node")
        state["workflow_step"] = "consistency_check"
        
        try:
            # Analyze consistency across agent results
            agent_results = state.get("agent_results", {})
            
            # Calculate consistency score
            consistency_score = self._calculate_consistency_score(agent_results)
            
            # Identify conflicts
            conflicts = self._identify_conflicts(agent_results)
            
            state["consistency_results"] = {
                "score": consistency_score,
                "conflicts": conflicts,
                "agent_count": len(agent_results),
                "recommendations": self._generate_recommendations(agent_results, conflicts)
            }
            
            logger.info(f"✅ Consistency check complete: score={consistency_score:.2f}, conflicts={len(conflicts)}")
        except Exception as e:
            logger.error(f"Error in consistency check: {e}")
            state["errors"].append(f"Consistency check error: {str(e)}")
        
        return state
    
    async def _research_node(self, state: WorkflowState) -> WorkflowState:
        """Research legal precedents"""
        logger.info("🔬 Research Node")
        state["workflow_step"] = "research"
        
        if self.precedent_reasoning_agent:
            try:
                query = state.get("contract_text", "")[:200]
                result = await self.precedent_reasoning_agent.cross_case_alignment(
                    query, "plaintiff", 5
                )
                state["agent_results"]["research"] = result
            except Exception as e:
                logger.error(f"Research error: {e}")
                state["errors"].append(f"Research error: {str(e)}")
        
        return state
    
    async def _draft_node(self, state: WorkflowState) -> WorkflowState:
        """Draft document based on research"""
        logger.info("✍️ Draft Node")
        state["workflow_step"] = "draft"
        
        # Draft logic would go here
        state["agent_results"]["draft"] = {"status": "drafted", "based_on_research": True}
        
        return state
    
    async def _review_node(self, state: WorkflowState) -> WorkflowState:
        """Review drafted document"""
        logger.info("📖 Review Node")
        state["workflow_step"] = "review"
        
        # Review logic would go here
        state["agent_results"]["review"] = {"status": "reviewed", "approved": True}
        
        return state
    
    async def _clause_analysis_node(self, state: WorkflowState) -> WorkflowState:
        """Analyze clause from different perspective"""
        logger.info("📄 Clause Analysis Node")
        state["workflow_step"] = "clause_analysis"
        
        # Additional clause analysis
        state["agent_results"]["clause_analysis"] = {"status": "analyzed"}
        
        return state
    
    async def _consistency_analysis_node(self, state: WorkflowState) -> WorkflowState:
        """Final consistency analysis"""
        return await self._consistency_check_node(state)
    
    # Helper methods
    def _route_by_risk_level(self, state: WorkflowState) -> str:
        """Route workflow based on risk level"""
        risk_level = state.get("risk_level", "low")
        return risk_level.lower()
    
    def _calculate_consistency_score(self, agent_results: Dict[str, Any]) -> float:
        """Calculate consistency score across agent results"""
        if len(agent_results) < 2:
            return 1.0
        
        # Extract risk scores if available
        risk_scores = []
        for agent, result in agent_results.items():
            if isinstance(result, dict) and "risk_score" in result:
                risk_scores.append(result["risk_score"])
            elif isinstance(result, dict) and "risk_level" in result:
                # Convert risk level to score
                level = result["risk_level"].lower()
                scores = {"critical": 0.9, "high": 0.7, "medium": 0.5, "low": 0.3}
                risk_scores.append(scores.get(level, 0.5))
        
        if len(risk_scores) < 2:
            return 0.8
        
        # Calculate variance (lower variance = higher consistency)
        import statistics
        if len(risk_scores) > 1:
            variance = statistics.variance(risk_scores)
            consistency = max(0.0, 1.0 - (variance * 2))
            return consistency
        
        return 0.8
    
    def _identify_conflicts(self, agent_results: Dict[str, Any]) -> List[str]:
        """Identify conflicts between agent results"""
        conflicts = []
        
        risk_levels = []
        for agent, result in agent_results.items():
            if isinstance(result, dict) and "risk_level" in result:
                risk_levels.append((agent, result["risk_level"]))
        
        if len(risk_levels) >= 2:
            levels = [level for _, level in risk_levels]
            if "critical" in levels and "low" in levels:
                conflicts.append("Conflicting risk levels: critical vs low")
            elif "high" in levels and "low" in levels:
                conflicts.append("Conflicting risk levels: high vs low")
        
        return conflicts
    
    def _generate_recommendations(
        self,
        agent_results: Dict[str, Any],
        conflicts: List[str]
    ) -> List[str]:
        """Generate recommendations based on consistency check"""
        recommendations = []
        
        if conflicts:
            recommendations.append("Review conflicting assessments - manual review recommended")
            recommendations.append("Consider running additional analysis to resolve conflicts")
        else:
            recommendations.append("Agent assessments are consistent")
        
        high_risk_count = sum(
            1 for result in agent_results.values()
            if isinstance(result, dict) and result.get("risk_level", "").lower() in ["high", "critical"]
        )
        
        if high_risk_count == len(agent_results):
            recommendations.append("All agents agree on high risk - immediate review required")
        elif high_risk_count > 0:
            recommendations.append(f"{high_risk_count} of {len(agent_results)} agents identified high risk")
        
        return recommendations
    
    # Public API methods
    async def comprehensive_analysis(
        self,
        contract_text: str,
        jurisdiction: str = "US"
    ) -> Dict[str, Any]:
        """
        Run comprehensive analysis workflow
        
        Args:
            contract_text: Contract text to analyze
            jurisdiction: Jurisdiction for analysis
            
        Returns:
            Complete analysis results
        """
        logger.info("🎯 Running comprehensive analysis workflow...")
        
        if not self.comprehensive_workflow:
            return {
                "error": "Workflow not available",
                "message": "LangGraph workflow not initialized"
            }
        
        try:
            # Initialize state
            initial_state: WorkflowState = {
                "contract_text": contract_text,
                "jurisdiction": jurisdiction,
                "risk_score": None,
                "risk_level": None,
                "risk_issues": [],
                "compliance_issues": [],
                "missing_clauses": [],
                "generated_clauses": {},
                "consistency_results": {},
                "agent_results": {},
                "workflow_step": "start",
                "errors": []
            }
            
            # Run workflow
            final_state = await self.comprehensive_workflow.ainvoke(initial_state)
            
            return {
                "status": "success",
                "contract_preview": contract_text[:200] + "...",
                "jurisdiction": jurisdiction,
                "risk_analysis": {
                    "level": final_state.get("risk_level"),
                    "score": final_state.get("risk_score"),
                    "issues": final_state.get("risk_issues", [])
                },
                "compliance": {
                    "issues": final_state.get("compliance_issues", [])
                },
                "missing_clauses": final_state.get("missing_clauses", []),
                "generated_clauses": final_state.get("generated_clauses", {}),
                "consistency": final_state.get("consistency_results", {}),
                "workflow_steps": final_state.get("workflow_step"),
                "errors": final_state.get("errors", [])
            }
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            return {
                "error": str(e),
                "message": "Workflow execution failed"
            }
    
    async def research_and_draft(
        self,
        query: str,
        document_type: str = "contract"
    ) -> Dict[str, Any]:
        """
        Run research → draft → review workflow
        
        Args:
            query: Research query
            document_type: Type of document to draft
            
        Returns:
            Workflow results
        """
        logger.info(f"🔄 Running research → draft workflow...")
        
        if not self.research_draft_workflow:
            return {
                "error": "Workflow not available",
                "message": "LangGraph workflow not initialized"
            }
        
        try:
            initial_state: WorkflowState = {
                "contract_text": query,
                "jurisdiction": "US",
                "risk_score": None,
                "risk_level": None,
                "risk_issues": [],
                "compliance_issues": [],
                "missing_clauses": [],
                "generated_clauses": {},
                "consistency_results": {},
                "agent_results": {},
                "workflow_step": "start",
                "errors": []
            }
            
            final_state = await self.research_draft_workflow.ainvoke(initial_state)
            
            return {
                "status": "success",
                "query": query,
                "document_type": document_type,
                "workflow_result": final_state.get("agent_results", {}),
                "workflow_steps": final_state.get("workflow_step"),
                "errors": final_state.get("errors", [])
            }
        except Exception as e:
            logger.error(f"Error in research-draft workflow: {e}")
            return {
                "error": str(e),
                "message": "Workflow execution failed"
            }
    
    async def cross_consistency_check(
        self,
        clause_text: str,
        jurisdiction: str = "US"
    ) -> Dict[str, Any]:
        """
        Run cross-consistency check workflow
        
        Args:
            clause_text: Clause to analyze
            jurisdiction: Jurisdiction for analysis
            
        Returns:
            Consistency check results
        """
        logger.info("🔍 Running cross-consistency check workflow...")
        
        if not self.consistency_check_workflow:
            return {
                "error": "Workflow not available",
                "message": "LangGraph workflow not initialized"
            }
        
        try:
            initial_state: WorkflowState = {
                "contract_text": clause_text,
                "jurisdiction": jurisdiction,
                "risk_score": None,
                "risk_level": None,
                "risk_issues": [],
                "compliance_issues": [],
                "missing_clauses": [],
                "generated_clauses": {},
                "consistency_results": {},
                "agent_results": {},
                "workflow_step": "start",
                "errors": []
            }
            
            final_state = await self.consistency_check_workflow.ainvoke(initial_state)
            
            return {
                "status": "success",
                "clause_text": clause_text[:200] + "...",
                "jurisdiction": jurisdiction,
                "agent_results": final_state.get("agent_results", {}),
                "consistency": final_state.get("consistency_results", {}),
                "workflow_steps": final_state.get("workflow_step"),
                "errors": final_state.get("errors", [])
            }
        except Exception as e:
            logger.error(f"Error in consistency check: {e}")
            return {
                "error": str(e),
                "message": "Workflow execution failed"
            }

