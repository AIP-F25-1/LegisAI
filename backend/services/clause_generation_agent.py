"""
Clause Generation Agent Service
Generates missing standard clauses (e.g., confidentiality, force majeure)
"""

import logging
import asyncio
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class StandardClause:
    """Standard clause template"""
    clause_type: str
    name: str
    description: str
    template: str
    required_in: List[str]  # Contract types where this is typically required
    jurisdiction_variations: Dict[str, str]  # Jurisdiction-specific versions

class ClauseGenerationAgent:
    """Generates missing standard clauses for contracts"""
    
    def __init__(self, ollama_client=None, ollama_model: str = "llama3.1:8b", hybrid_retriever=None):
        """
        Initialize clause generation agent
        
        Args:
            ollama_client: Ollama client for AI generation
            ollama_model: Model name to use
            hybrid_retriever: HybridRetriever for finding similar clauses
        """
        self.ollama_client = ollama_client
        self.ollama_model = ollama_model
        self.hybrid_retriever = hybrid_retriever
        
        # Standard clause templates
        self.standard_clauses = self._load_standard_clauses()
    
    def _load_standard_clauses(self) -> Dict[str, StandardClause]:
        """Load standard clause templates"""
        return {
            "confidentiality": StandardClause(
                clause_type="confidentiality",
                name="Confidentiality Clause",
                description="Protects confidential information shared between parties",
                template="""CONFIDENTIALITY. Each party agrees to maintain the confidentiality of all proprietary and confidential information disclosed by the other party. Confidential information includes, but is not limited to, business plans, financial information, customer lists, and trade secrets. This obligation shall survive termination of this agreement for a period of [NUMBER] years.""",
                required_in=["service_agreement", "partnership", "joint_venture", "nda"],
                jurisdiction_variations={}
            ),
            "force_majeure": StandardClause(
                clause_type="force_majeure",
                name="Force Majeure Clause",
                description="Excuses performance due to unforeseen circumstances",
                template="""FORCE MAJEURE. Neither party shall be liable for any failure or delay in performance under this agreement due to circumstances beyond its reasonable control, including but not limited to acts of God, natural disasters, war, terrorism, labor strikes, or government actions. The affected party shall notify the other party promptly and use reasonable efforts to resume performance.""",
                required_in=["service_agreement", "supply_agreement", "partnership"],
                jurisdiction_variations={}
            ),
            "termination": StandardClause(
                clause_type="termination",
                name="Termination Clause",
                description="Specifies conditions and procedures for contract termination",
                template="""TERMINATION. This agreement may be terminated: (a) by either party upon [NUMBER] days written notice; (b) immediately upon material breach by the other party that remains uncured for [NUMBER] days after written notice; (c) upon insolvency or bankruptcy of either party. Upon termination, all obligations shall cease except those that by their nature survive termination.""",
                required_in=["service_agreement", "employment", "partnership"],
                jurisdiction_variations={}
            ),
            "indemnification": StandardClause(
                clause_type="indemnification",
                name="Indemnification Clause",
                description="Specifies liability and indemnification obligations",
                template="""INDEMNIFICATION. Each party agrees to indemnify, defend, and hold harmless the other party from and against any claims, damages, losses, or expenses (including reasonable attorney fees) arising from: (a) breach of this agreement; (b) negligence or willful misconduct; (c) violation of applicable laws. This indemnification obligation shall survive termination of this agreement.""",
                required_in=["service_agreement", "partnership", "vendor_agreement"],
                jurisdiction_variations={}
            ),
            "governing_law": StandardClause(
                clause_type="governing_law",
                name="Governing Law and Jurisdiction",
                description="Specifies applicable law and dispute resolution",
                template="""GOVERNING LAW AND JURISDICTION. This agreement shall be governed by and construed in accordance with the laws of [JURISDICTION], without regard to its conflict of law principles. Any disputes arising under this agreement shall be resolved in the courts of [JURISDICTION], and both parties consent to the exclusive jurisdiction of such courts.""",
                required_in=["all"],
                jurisdiction_variations={}
            ),
            "dispute_resolution": StandardClause(
                clause_type="dispute_resolution",
                name="Dispute Resolution",
                description="Specifies methods for resolving disputes",
                template="""DISPUTE RESOLUTION. Any dispute arising under this agreement shall first be addressed through good faith negotiation between the parties. If negotiation fails, disputes shall be resolved through [ARBITRATION/MEDIATION] in accordance with the rules of [ARBITRATION_BODY]. The decision of the arbitrator/mediator shall be final and binding.""",
                required_in=["service_agreement", "partnership", "commercial"],
                jurisdiction_variations={}
            ),
            "intellectual_property": StandardClause(
                clause_type="intellectual_property",
                name="Intellectual Property Rights",
                description="Defines ownership and rights to intellectual property",
                template="""INTELLECTUAL PROPERTY. All intellectual property rights, including but not limited to copyrights, trademarks, patents, and trade secrets, created or developed under this agreement shall be owned by [PARTY]. Each party retains ownership of its pre-existing intellectual property. No license is granted except as expressly set forth in this agreement.""",
                required_in=["service_agreement", "development", "consulting"],
                jurisdiction_variations={}
            ),
            "limitation_of_liability": StandardClause(
                clause_type="limitation_of_liability",
                name="Limitation of Liability",
                description="Limits liability exposure",
                template="""LIMITATION OF LIABILITY. To the maximum extent permitted by law, neither party shall be liable for any indirect, incidental, special, or consequential damages, including lost profits, even if advised of the possibility of such damages. Each party's total liability shall not exceed [AMOUNT] or the amount paid under this agreement in the [TIME_PERIOD] preceding the claim, whichever is greater.""",
                required_in=["service_agreement", "software_license", "vendor_agreement"],
                jurisdiction_variations={}
            )
        }
    
    def detect_missing_clauses(self, contract_text: str, contract_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Detect which standard clauses are missing from a contract
        
        Args:
            contract_text: Text of the contract to analyze
            contract_type: Optional contract type (e.g., "service_agreement", "partnership")
            
        Returns:
            List of missing standard clauses
        """
        logger.info(f"🔍 Detecting missing standard clauses...")
        
        contract_lower = contract_text.lower()
        missing_clauses = []
        
        # Check each standard clause
        for clause_type, clause in self.standard_clauses.items():
            # Check if clause is present
            is_present = self._check_clause_presence(contract_lower, clause)
            
            if not is_present:
                # Check if clause is required for this contract type
                is_required = (
                    contract_type in clause.required_in or
                    "all" in clause.required_in or
                    contract_type is None
                )
                
                missing_clauses.append({
                    "clause_type": clause_type,
                    "name": clause.name,
                    "description": clause.description,
                    "is_required": is_required,
                    "template": clause.template,
                    "priority": "high" if is_required else "medium"
                })
        
        # Sort by priority
        missing_clauses.sort(key=lambda x: (x["priority"] == "high", x["name"]))
        
        return missing_clauses
    
    def _check_clause_presence(self, contract_text: str, clause: StandardClause) -> bool:
        """Check if a standard clause is present in the contract"""
        # Check for keywords related to the clause type
        keywords = {
            "confidentiality": ["confidential", "non-disclosure", "proprietary information", "trade secret"],
            "force_majeure": ["force majeure", "act of god", "unforeseen circumstances", "beyond control"],
            "termination": ["termination", "terminate", "expiration", "end of agreement"],
            "indemnification": ["indemnify", "indemnification", "hold harmless", "defend"],
            "governing_law": ["governing law", "jurisdiction", "applicable law", "laws of"],
            "dispute_resolution": ["dispute resolution", "arbitration", "mediation", "dispute"],
            "intellectual_property": ["intellectual property", "copyright", "patent", "trademark", "ip rights"],
            "limitation_of_liability": ["limitation of liability", "liability cap", "maximum liability", "exclude liability"]
        }
        
        clause_keywords = keywords.get(clause.clause_type, [])
        for keyword in clause_keywords:
            if keyword in contract_text:
                return True
        
        return False
    
    async def generate_clause(
        self,
        clause_type: str,
        contract_context: Optional[str] = None,
        jurisdiction: str = "US",
        custom_requirements: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a standard clause with customization
        
        Args:
            clause_type: Type of clause to generate (e.g., "confidentiality", "force_majeure")
            contract_context: Optional context from the contract for customization
            jurisdiction: Jurisdiction for jurisdiction-specific variations
            custom_requirements: Optional custom requirements to include
            
        Returns:
            Generated clause with metadata
        """
        logger.info(f"📝 Generating {clause_type} clause...")
        
        if clause_type not in self.standard_clauses:
            return {
                "error": f"Unknown clause type: {clause_type}",
                "available_types": list(self.standard_clauses.keys())
            }
        
        standard_clause = self.standard_clauses[clause_type]
        base_template = standard_clause.template
        
        # Customize using AI if available
        if self.ollama_client and (contract_context or custom_requirements):
            customized_clause = await self._customize_clause_with_ai(
                base_template,
                clause_type,
                contract_context,
                jurisdiction,
                custom_requirements
            )
            if customized_clause:
                base_template = customized_clause
        
        # Try to find similar clauses from corpus
        similar_clauses = []
        if self.hybrid_retriever:
            try:
                search_query = f"{clause_type} clause {standard_clause.name.lower()}"
                results = self.hybrid_retriever.search(
                    search_query,
                    k=3,
                    semantic_weight=0.7,
                    keyword_weight=0.3
                )
                for result in results:
                    similar_clauses.append({
                        "text": result.get('text', '')[:300],
                        "score": result.get('combined_score', 0),
                        "source": result.get('metadata', {}).get('title', 'Unknown')
                    })
            except Exception as e:
                logger.warning(f"Error finding similar clauses: {e}")
        
        return {
            "clause_type": clause_type,
            "name": standard_clause.name,
            "description": standard_clause.description,
            "generated_clause": base_template,
            "jurisdiction": jurisdiction,
            "similar_clauses": similar_clauses,
            "customized": contract_context is not None or custom_requirements is not None
        }
    
    async def _customize_clause_with_ai(
        self,
        template: str,
        clause_type: str,
        contract_context: Optional[str],
        jurisdiction: str,
        custom_requirements: Optional[str]
    ) -> Optional[str]:
        """Customize clause using AI"""
        try:
            prompt = f"""Customize the following standard {clause_type} clause for a contract.

BASE TEMPLATE:
{template}

"""
            if contract_context:
                prompt += f"CONTRACT CONTEXT:\n{contract_context[:1000]}\n\n"
            
            if custom_requirements:
                prompt += f"CUSTOM REQUIREMENTS:\n{custom_requirements}\n\n"
            
            prompt += f"JURISDICTION: {jurisdiction}\n\n"
            prompt += "Generate a customized version of this clause that fits the contract context and requirements. Maintain legal accuracy and enforceability."
            
            # Use AI to generate (similar to summarization agent pattern)
            if hasattr(self.ollama_client, 'generate') and asyncio.iscoroutinefunction(self.ollama_client.generate):
                response = await self.ollama_client.generate(
                    model=self.ollama_model,
                    prompt=prompt,
                    options={
                        'temperature': 0.5,
                        'top_p': 0.9,
                        'num_predict': 800
                    }
                )
                if hasattr(response, 'response'):
                    return response.response
                elif isinstance(response, dict):
                    return response.get('response', '')
            else:
                # Sync client
                loop = asyncio.get_event_loop()
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = loop.run_in_executor(
                        executor,
                        lambda: self.ollama_client.generate(
                            model=self.ollama_model,
                            prompt=prompt,
                            options={
                                'temperature': 0.5,
                                'top_p': 0.9,
                                'num_predict': 800
                            }
                        )
                    )
                    response = await asyncio.wait_for(future, timeout=60.0)
                    if hasattr(response, 'response'):
                        return response.response
                    elif isinstance(response, dict):
                        return response.get('response', '')
            
            return None
        except Exception as e:
            logger.warning(f"AI customization failed: {e}")
            return None
    
    async def generate_all_missing_clauses(
        self,
        contract_text: str,
        contract_type: Optional[str] = None,
        jurisdiction: str = "US"
    ) -> Dict[str, Any]:
        """
        Detect and generate all missing standard clauses
        
        Args:
            contract_text: Text of the contract
            contract_type: Optional contract type
            jurisdiction: Jurisdiction for customization
            
        Returns:
            Dictionary with missing clauses and generated versions
        """
        logger.info(f"📋 Generating all missing standard clauses...")
        
        # Detect missing clauses
        missing = self.detect_missing_clauses(contract_text, contract_type)
        
        # Generate each missing clause
        generated_clauses = []
        for missing_clause in missing:
            clause = await self.generate_clause(
                clause_type=missing_clause["clause_type"],
                contract_context=contract_text[:2000],  # Use contract as context
                jurisdiction=jurisdiction
            )
            generated_clauses.append({
                **clause,
                "priority": missing_clause["priority"],
                "is_required": missing_clause["is_required"]
            })
        
        return {
            "total_missing": len(missing),
            "required_missing": len([c for c in missing if c["is_required"]]),
            "optional_missing": len([c for c in missing if not c["is_required"]]),
            "generated_clauses": generated_clauses
        }

