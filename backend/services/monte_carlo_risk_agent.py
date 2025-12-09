"""
Monte Carlo Risk Agent Service
Simulates "what if" scenarios (counterparty defaults, breach, etc.)
"""

import logging
import asyncio
import random
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import math

logger = logging.getLogger(__name__)

@dataclass
class ScenarioResult:
    """Result of a Monte Carlo simulation scenario"""
    scenario_name: str
    probability: float  # 0.0 to 1.0
    impact_score: float  # 0.0 to 1.0
    expected_loss: float
    risk_level: str  # "low", "medium", "high", "critical"
    outcomes: List[Dict[str, Any]]
    recommendations: List[str]

@dataclass
class SimulationRun:
    """Single Monte Carlo simulation run"""
    run_id: int
    scenario: str
    outcome: str
    loss_amount: float
    probability: float
    factors: Dict[str, Any]

class MonteCarloRiskAgent:
    """Simulates risk scenarios using Monte Carlo methods"""
    
    def __init__(self, clause_analyzer=None, ollama_client=None, ollama_model: str = "llama3.1:8b"):
        """
        Initialize Monte Carlo risk agent
        
        Args:
            clause_analyzer: ClauseAnalyzer for risk assessment
            ollama_client: Ollama client for AI analysis
            ollama_model: Model name to use
        """
        self.clause_analyzer = clause_analyzer
        self.ollama_client = ollama_client
        self.ollama_model = ollama_model
        
        # Default scenario probabilities (can be customized)
        self.default_probabilities = {
            "counterparty_default": 0.05,  # 5% base probability
            "breach_of_contract": 0.10,   # 10% base probability
            "payment_delay": 0.15,        # 15% base probability
            "force_majeure": 0.03,        # 3% base probability
            "regulatory_change": 0.08,    # 8% base probability
            "intellectual_property_dispute": 0.04,  # 4% base probability
            "data_breach": 0.06,          # 6% base probability
            "termination": 0.12           # 12% base probability
        }
    
    async def simulate_scenarios(
        self,
        contract_text: str,
        scenarios: Optional[List[str]] = None,
        num_simulations: int = 1000,
        jurisdiction: str = "US"
    ) -> Dict[str, Any]:
        """
        Run Monte Carlo simulations for various "what if" scenarios
        
        Args:
            contract_text: Contract text to analyze
            scenarios: List of scenarios to simulate (None = all)
            num_simulations: Number of Monte Carlo iterations
            jurisdiction: Jurisdiction for risk assessment
            
        Returns:
            Dictionary with simulation results for each scenario
        """
        logger.info(f"🎲 Running Monte Carlo simulations ({num_simulations} iterations)...")
        
        if scenarios is None:
            scenarios = list(self.default_probabilities.keys())
        
        results = {}
        
        for scenario in scenarios:
            logger.info(f"   Simulating scenario: {scenario}")
            scenario_result = await self._simulate_single_scenario(
                contract_text,
                scenario,
                num_simulations,
                jurisdiction
            )
            results[scenario] = self._scenario_result_to_dict(scenario_result)
        
        # Calculate overall risk metrics
        overall_risk = self._calculate_overall_risk(results)
        
        return {
            "contract_analyzed": contract_text[:200] + "..." if len(contract_text) > 200 else contract_text,
            "jurisdiction": jurisdiction,
            "num_simulations": num_simulations,
            "scenarios_simulated": scenarios,
            "scenario_results": results,
            "overall_risk": overall_risk,
            "recommendations": self._generate_overall_recommendations(results)
        }
    
    async def _simulate_single_scenario(
        self,
        contract_text: str,
        scenario: str,
        num_simulations: int,
        jurisdiction: str
    ) -> ScenarioResult:
        """Run Monte Carlo simulation for a single scenario"""
        
        # Get base probability
        base_probability = self.default_probabilities.get(scenario, 0.05)
        
        # Adjust probability based on contract risk
        if self.clause_analyzer:
            # Analyze contract for risk factors
            risk_analysis = self.clause_analyzer.analyze_document(contract_text, jurisdiction)
            avg_risk_score = sum(
                clause.get('risk_score', 0.5) 
                for clause in risk_analysis.get('clauses', [])
            ) / max(len(risk_analysis.get('clauses', [])), 1)
            
            # Higher risk contracts = higher probability of issues
            adjusted_probability = base_probability * (1 + avg_risk_score)
            adjusted_probability = min(adjusted_probability, 0.95)  # Cap at 95%
        else:
            adjusted_probability = base_probability
        
        # Run Monte Carlo simulations
        outcomes = []
        total_loss = 0.0
        positive_outcomes = 0
        
        for i in range(num_simulations):
            # Simulate outcome
            outcome = self._simulate_outcome(scenario, contract_text, adjusted_probability)
            outcomes.append(outcome)
            
            if outcome['occurred']:
                positive_outcomes += 1
                total_loss += outcome.get('loss_amount', 0.0)
        
        # Calculate statistics
        actual_probability = positive_outcomes / num_simulations
        expected_loss = total_loss / num_simulations
        
        # Determine impact score
        impact_score = self._calculate_impact_score(outcomes, scenario)
        
        # Determine risk level
        risk_level = self._determine_risk_level(actual_probability, impact_score)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(
            scenario,
            actual_probability,
            impact_score,
            contract_text
        )
        
        return ScenarioResult(
            scenario_name=scenario,
            probability=actual_probability,
            impact_score=impact_score,
            expected_loss=expected_loss,
            risk_level=risk_level,
            outcomes=outcomes[:10],  # Sample outcomes
            recommendations=recommendations
        )
    
    def _simulate_outcome(
        self,
        scenario: str,
        contract_text: str,
        probability: float
    ) -> Dict[str, Any]:
        """Simulate a single outcome for a scenario"""
        occurred = random.random() < probability
        
        outcome = {
            "occurred": occurred,
            "scenario": scenario,
            "factors": {}
        }
        
        if occurred:
            # Simulate impact
            if scenario == "counterparty_default":
                outcome["loss_amount"] = random.uniform(10000, 500000)
                outcome["factors"] = {
                    "default_reason": random.choice(["insolvency", "breach", "force_majeure"]),
                    "recovery_probability": random.uniform(0.1, 0.5)
                }
            elif scenario == "breach_of_contract":
                outcome["loss_amount"] = random.uniform(5000, 200000)
                outcome["factors"] = {
                    "breach_type": random.choice(["material", "minor", "anticipatory"]),
                    "remedy_available": random.choice(["damages", "specific_performance", "termination"])
                }
            elif scenario == "payment_delay":
                outcome["loss_amount"] = random.uniform(1000, 50000)
                outcome["factors"] = {
                    "delay_days": random.randint(30, 180),
                    "interest_applicable": random.choice([True, False])
                }
            elif scenario == "force_majeure":
                outcome["loss_amount"] = random.uniform(0, 100000)
                outcome["factors"] = {
                    "event_type": random.choice(["natural_disaster", "pandemic", "war", "government_action"]),
                    "duration_weeks": random.randint(2, 26)
                }
            elif scenario == "data_breach":
                outcome["loss_amount"] = random.uniform(50000, 500000)
                outcome["factors"] = {
                    "records_affected": random.randint(100, 100000),
                    "notification_required": True,
                    "regulatory_fine_risk": random.uniform(0.3, 0.8)
                }
            elif scenario == "termination":
                outcome["loss_amount"] = random.uniform(10000, 300000)
                outcome["factors"] = {
                    "termination_reason": random.choice(["for_cause", "convenience", "breach"]),
                    "notice_period_days": random.randint(0, 90)
                }
            else:
                outcome["loss_amount"] = random.uniform(5000, 100000)
                outcome["factors"] = {"generic_scenario": True}
        else:
            outcome["loss_amount"] = 0.0
        
        return outcome
    
    def _calculate_impact_score(self, outcomes: List[Dict[str, Any]], scenario: str) -> float:
        """Calculate impact score based on outcomes"""
        if not outcomes:
            return 0.0
        
        occurred_outcomes = [o for o in outcomes if o.get('occurred', False)]
        if not occurred_outcomes:
            return 0.0
        
        # Calculate average loss (normalized)
        avg_loss = sum(o.get('loss_amount', 0) for o in occurred_outcomes) / len(occurred_outcomes)
        
        # Normalize to 0-1 scale (assuming max loss of 1M)
        normalized_loss = min(avg_loss / 1000000, 1.0)
        
        # Factor in frequency
        frequency = len(occurred_outcomes) / len(outcomes)
        
        # Combined impact score
        impact_score = (normalized_loss * 0.7) + (frequency * 0.3)
        
        return min(impact_score, 1.0)
    
    def _determine_risk_level(self, probability: float, impact_score: float) -> str:
        """Determine overall risk level"""
        # Risk = Probability × Impact
        risk_score = probability * impact_score
        
        if risk_score >= 0.7:
            return "critical"
        elif risk_score >= 0.5:
            return "high"
        elif risk_score >= 0.3:
            return "medium"
        else:
            return "low"
    
    async def _generate_recommendations(
        self,
        scenario: str,
        probability: float,
        impact_score: float,
        contract_text: str
    ) -> List[str]:
        """Generate recommendations based on simulation results"""
        recommendations = []
        
        # Base recommendations
        if probability > 0.2:
            recommendations.append(f"High probability ({probability:.1%}) of {scenario}. Consider risk mitigation measures.")
        
        if impact_score > 0.5:
            recommendations.append(f"High impact scenario. Implement protective clauses and insurance.")
        
        # Scenario-specific recommendations
        if scenario == "counterparty_default":
            recommendations.extend([
                "Include credit checks and financial guarantees",
                "Add early warning triggers for financial distress",
                "Consider escrow arrangements for payments"
            ])
        elif scenario == "breach_of_contract":
            recommendations.extend([
                "Define clear breach conditions and remedies",
                "Include liquidated damages clauses",
                "Specify dispute resolution procedures"
            ])
        elif scenario == "payment_delay":
            recommendations.extend([
                "Include late payment penalties",
                "Add payment milestones and triggers",
                "Consider advance payment requirements"
            ])
        elif scenario == "data_breach":
            recommendations.extend([
                "Include data security requirements",
                "Add breach notification obligations",
                "Specify liability caps for data breaches"
            ])
        
        # Use AI for additional recommendations if available
        if self.ollama_client and len(recommendations) < 5:
            try:
                ai_recommendations = await self._get_ai_recommendations(
                    scenario, probability, impact_score, contract_text
                )
                recommendations.extend(ai_recommendations[:3])
            except Exception as e:
                logger.warning(f"AI recommendations failed: {e}")
        
        return recommendations[:6]  # Limit to 6 recommendations
    
    async def _get_ai_recommendations(
        self,
        scenario: str,
        probability: float,
        impact_score: float,
        contract_text: str
    ) -> List[str]:
        """Get AI-powered recommendations"""
        prompt = f"""Based on Monte Carlo simulation results, provide risk mitigation recommendations:

SCENARIO: {scenario}
PROBABILITY: {probability:.1%}
IMPACT SCORE: {impact_score:.2f}
CONTRACT CONTEXT: {contract_text[:500]}

Provide 3-5 specific, actionable recommendations to mitigate this risk.
Format as a numbered list."""
        
        try:
            if hasattr(self.ollama_client, 'generate') and asyncio.iscoroutinefunction(self.ollama_client.generate):
                response = await self.ollama_client.generate(
                    model=self.ollama_model,
                    prompt=prompt,
                    options={'temperature': 0.5, 'top_p': 0.9, 'num_predict': 400}
                )
                text = response.response if hasattr(response, 'response') else str(response)
            else:
                loop = asyncio.get_event_loop()
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = loop.run_in_executor(
                        executor,
                        lambda: self.ollama_client.generate(
                            model=self.ollama_model,
                            prompt=prompt,
                            options={'temperature': 0.5, 'top_p': 0.9, 'num_predict': 400}
                        )
                    )
                    response = await asyncio.wait_for(future, timeout=60.0)
                    text = response.response if hasattr(response, 'response') else str(response)
            
            # Parse recommendations
            recommendations = []
            for line in text.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    content = re.sub(r'^[\d\-•\.\s]+', '', line).strip()
                    if content:
                        recommendations.append(content)
            
            return recommendations
        except Exception as e:
            logger.warning(f"Error getting AI recommendations: {e}")
            return []
    
    def _calculate_overall_risk(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall risk metrics from all scenarios"""
        if not results:
            return {
                "overall_risk_score": 0.0,
                "highest_risk_scenario": None,
                "expected_total_loss": 0.0,
                "risk_level": "low"
            }
        
        # Calculate weighted risk score
        total_risk = 0.0
        total_loss = 0.0
        max_risk = 0.0
        highest_risk_scenario = None
        
        for scenario, result in results.items():
            prob = result.get('probability', 0.0)
            impact = result.get('impact_score', 0.0)
            loss = result.get('expected_loss', 0.0)
            
            risk_score = prob * impact
            total_risk += risk_score
            total_loss += loss
            
            if risk_score > max_risk:
                max_risk = risk_score
                highest_risk_scenario = scenario
        
        avg_risk = total_risk / len(results) if results else 0.0
        
        # Determine overall risk level
        if avg_risk >= 0.7:
            risk_level = "critical"
        elif avg_risk >= 0.5:
            risk_level = "high"
        elif avg_risk >= 0.3:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "overall_risk_score": avg_risk,
            "highest_risk_scenario": highest_risk_scenario,
            "expected_total_loss": total_loss,
            "risk_level": risk_level,
            "scenarios_analyzed": len(results)
        }
    
    def _generate_overall_recommendations(self, results: Dict[str, Dict[str, Any]]) -> List[str]:
        """Generate overall recommendations based on all scenarios"""
        recommendations = []
        
        # Find high-risk scenarios
        high_risk = [
            (scenario, result) 
            for scenario, result in results.items() 
            if result.get('risk_level') in ['high', 'critical']
        ]
        
        if high_risk:
            recommendations.append(
                f"Address {len(high_risk)} high-risk scenarios identified in simulation"
            )
        
        # Find scenarios with high probability
        high_prob = [
            scenario 
            for scenario, result in results.items() 
            if result.get('probability', 0) > 0.2
        ]
        
        if high_prob:
            recommendations.append(
                f"Focus risk mitigation on: {', '.join(high_prob[:3])}"
            )
        
        # General recommendations
        recommendations.extend([
            "Review and strengthen contract terms for identified risk scenarios",
            "Consider insurance coverage for high-impact scenarios",
            "Implement monitoring and early warning systems"
        ])
        
        return recommendations[:5]
    
    def _scenario_result_to_dict(self, result: ScenarioResult) -> Dict[str, Any]:
        """Convert ScenarioResult to dictionary"""
        return {
            "scenario_name": result.scenario_name,
            "probability": result.probability,
            "impact_score": result.impact_score,
            "expected_loss": result.expected_loss,
            "risk_level": result.risk_level,
            "sample_outcomes": result.outcomes[:5],
            "recommendations": result.recommendations
        }

