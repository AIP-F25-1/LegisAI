"""
Redlining & Comparison Agent Service
ML-based clause alignment across two contracts with risk-focused change detection
"""

import logging
import asyncio
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

@dataclass
class ClauseAlignment:
    """Alignment between clauses from two contracts"""
    clause1_text: str
    clause2_text: str
    similarity_score: float  # 0.0 to 1.0
    alignment_type: str  # "matched", "modified", "added", "removed", "unmatched"
    clause1_index: int
    clause2_index: int
    semantic_similarity: float

@dataclass
class RiskChange:
    """Risk-focused change detection"""
    change_type: str  # "risk_increased", "risk_decreased", "risk_introduced", "risk_removed", "neutral"
    clause_text: str
    risk_score_delta: float  # Change in risk score
    old_risk_level: Optional[str]
    new_risk_level: Optional[str]
    risk_factors: List[str]
    recommendation: str

class RedliningComparisonAgent:
    """Compares two contracts with ML-based clause alignment and risk analysis"""
    
    def __init__(self, clause_analyzer=None, ollama_client=None, ollama_model: str = "llama3.1:8b", embeddings_model=None):
        """
        Initialize redlining comparison agent
        
        Args:
            clause_analyzer: ClauseAnalyzer instance for risk detection
            ollama_client: Ollama client for AI analysis
            ollama_model: Model name to use
            embeddings_model: Embeddings model for semantic similarity
        """
        self.clause_analyzer = clause_analyzer
        self.ollama_client = ollama_client
        self.ollama_model = ollama_model
        self.embeddings_model = embeddings_model
    
    def _extract_clauses(self, contract_text: str) -> List[Dict[str, Any]]:
        """Extract clauses from contract text"""
        clauses = []
        
        # Pattern 1: Numbered clauses (1., 2., etc.)
        numbered_pattern = r'(\d+\.)\s*([A-Z][^0-9]+?)(?=\d+\.|$)'
        matches = re.finditer(numbered_pattern, contract_text, re.MULTILINE | re.DOTALL)
        for match in matches:
            clause_num = match.group(1)
            clause_text = match.group(2).strip()
            if len(clause_text) > 20:  # Only include substantial clauses
                clauses.append({
                    "number": clause_num,
                    "text": clause_text,
                    "index": len(clauses)
                })
        
        # Pattern 2: Section headers (SECTION 1, Article I, etc.)
        section_pattern = r'(?:SECTION|Article|Clause)\s+[IVX\d]+[.:]\s*([A-Z][^A-Z]+?)(?=(?:SECTION|Article|Clause)\s+[IVX\d]+|$)'
        matches = re.finditer(section_pattern, contract_text, re.MULTILINE | re.DOTALL)
        for match in matches:
            clause_text = match.group(1).strip()
            if len(clause_text) > 20:
                clauses.append({
                    "number": f"Section {len(clauses) + 1}",
                    "text": clause_text,
                    "index": len(clauses)
                })
        
        # Pattern 3: Paragraph-based (if no clear structure, split by paragraphs)
        if not clauses:
            paragraphs = contract_text.split('\n\n')
            for i, para in enumerate(paragraphs):
                para = para.strip()
                if len(para) > 50:  # Substantial paragraphs
                    clauses.append({
                        "number": f"Para {i + 1}",
                        "text": para,
                        "index": i
                    })
        
        return clauses
    
    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity using embeddings if available"""
        if self.embeddings_model:
            try:
                embeddings = self.embeddings_model.encode([text1, text2])
                # Cosine similarity
                import numpy as np
                similarity = np.dot(embeddings[0], embeddings[1]) / (
                    np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
                )
                return float(similarity)
            except Exception as e:
                logger.warning(f"Error calculating semantic similarity: {e}")
        
        # Fallback to sequence matcher
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    async def align_clauses(
        self,
        contract1_text: str,
        contract2_text: str,
        contract1_name: Optional[str] = None,
        contract2_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        ML-based clause alignment across two contracts
        
        Args:
            contract1_text: Text of first contract (original)
            contract2_text: Text of second contract (revised)
            contract1_name: Optional name for contract 1
            contract2_name: Optional name for contract 2
            
        Returns:
            Dictionary with aligned clauses and change analysis
        """
        logger.info(f"🔍 Aligning clauses between two contracts...")
        
        # Extract clauses from both contracts
        clauses1 = self._extract_clauses(contract1_text)
        clauses2 = self._extract_clauses(contract2_text)
        
        logger.info(f"📄 Contract 1: {len(clauses1)} clauses, Contract 2: {len(clauses2)} clauses")
        
        # Align clauses using similarity matching
        alignments: List[ClauseAlignment] = []
        matched_indices2 = set()
        
        # Match clauses based on semantic similarity
        for i, clause1 in enumerate(clauses1):
            best_match = None
            best_score = 0.0
            best_index = -1
            
            for j, clause2 in enumerate(clauses2):
                if j in matched_indices2:
                    continue
                
                # Calculate similarity
                similarity = self._calculate_semantic_similarity(
                    clause1["text"],
                    clause2["text"]
                )
                
                if similarity > best_score and similarity > 0.3:  # Threshold
                    best_score = similarity
                    best_match = clause2
                    best_index = j
            
            if best_match:
                # Matched clause
                alignment_type = "modified" if best_score < 0.9 else "matched"
                alignments.append(ClauseAlignment(
                    clause1_text=clause1["text"],
                    clause2_text=best_match["text"],
                    similarity_score=best_score,
                    alignment_type=alignment_type,
                    clause1_index=i,
                    clause2_index=best_index,
                    semantic_similarity=best_score
                ))
                matched_indices2.add(best_index)
            else:
                # Removed clause (in contract1 but not in contract2)
                alignments.append(ClauseAlignment(
                    clause1_text=clause1["text"],
                    clause2_text="",
                    similarity_score=0.0,
                    alignment_type="removed",
                    clause1_index=i,
                    clause2_index=-1,
                    semantic_similarity=0.0
                ))
        
        # Find added clauses (in contract2 but not matched)
        for j, clause2 in enumerate(clauses2):
            if j not in matched_indices2:
                alignments.append(ClauseAlignment(
                    clause1_text="",
                    clause2_text=clause2["text"],
                    similarity_score=0.0,
                    alignment_type="added",
                    clause1_index=-1,
                    clause2_index=j,
                    semantic_similarity=0.0
                ))
        
        # Use AI for better alignment if available
        if self.ollama_client and len(alignments) > 0:
            # Refine alignments with AI
            refined_alignments = await self._refine_alignments_with_ai(
                alignments,
                contract1_name or "Contract 1",
                contract2_name or "Contract 2"
            )
            if refined_alignments:
                alignments = refined_alignments
        
        return {
            "contract1_name": contract1_name or "Contract 1",
            "contract2_name": contract2_name or "Contract 2",
            "contract1_clauses": len(clauses1),
            "contract2_clauses": len(clauses2),
            "alignments": [self._alignment_to_dict(a) for a in alignments],
            "summary": {
                "matched": len([a for a in alignments if a.alignment_type == "matched"]),
                "modified": len([a for a in alignments if a.alignment_type == "modified"]),
                "added": len([a for a in alignments if a.alignment_type == "added"]),
                "removed": len([a for a in alignments if a.alignment_type == "removed"])
            }
        }
    
    async def _refine_alignments_with_ai(self, alignments: List[ClauseAlignment], name1: str, name2: str) -> Optional[List[ClauseAlignment]]:
        """Refine alignments using AI analysis"""
        try:
            # Sample a few alignments for AI analysis
            sample_alignments = alignments[:5]  # Analyze first 5
            
            prompt = f"""Analyze clause alignments between two contracts:

{name1} vs {name2}

Sample alignments:
"""
            for i, align in enumerate(sample_alignments):
                prompt += f"\n{i+1}. Type: {align.alignment_type}, Similarity: {align.similarity_score:.2f}\n"
                if align.clause1_text:
                    prompt += f"   Contract 1: {align.clause1_text[:200]}...\n"
                if align.clause2_text:
                    prompt += f"   Contract 2: {align.clause2_text[:200]}...\n"
            
            prompt += "\nProvide recommendations for improving alignment accuracy."
            
            # This is a placeholder - in production, you'd use the AI to refine
            # For now, return original alignments
            return alignments
        except Exception as e:
            logger.warning(f"AI refinement failed: {e}")
            return alignments
    
    def _alignment_to_dict(self, alignment: ClauseAlignment) -> Dict[str, Any]:
        """Convert ClauseAlignment to dictionary"""
        return {
            "clause1_text": alignment.clause1_text[:500] if alignment.clause1_text else "",
            "clause2_text": alignment.clause2_text[:500] if alignment.clause2_text else "",
            "similarity_score": alignment.similarity_score,
            "alignment_type": alignment.alignment_type,
            "clause1_index": alignment.clause1_index,
            "clause2_index": alignment.clause2_index,
            "semantic_similarity": alignment.semantic_similarity
        }
    
    async def detect_risk_changes(
        self,
        contract1_text: str,
        contract2_text: str,
        jurisdiction: str = "US"
    ) -> Dict[str, Any]:
        """
        Risk-focused change detection (not just diff)
        
        Args:
            contract1_text: Text of original contract
            contract2_text: Text of revised contract
            jurisdiction: Jurisdiction for risk analysis
            
        Returns:
            Dictionary with risk changes detected
        """
        logger.info(f"⚠️ Detecting risk-focused changes between contracts...")
        
        if not self.clause_analyzer:
            return {
                "error": "Clause analyzer not available for risk detection",
                "risk_changes": []
            }
        
        # Align clauses first
        alignment_result = await self.align_clauses(contract1_text, contract2_text)
        alignments = alignment_result["alignments"]
        
        risk_changes: List[RiskChange] = []
        
        # Analyze each alignment for risk changes
        for align_dict in alignments:
            alignment_type = align_dict["alignment_type"]
            clause1_text = align_dict.get("clause1_text", "")
            clause2_text = align_dict.get("clause2_text", "")
            
            if alignment_type == "matched":
                # Check if risk changed even though clause is matched
                if clause1_text and clause2_text:
                    risk1 = self.clause_analyzer.analyze_clause(clause1_text, jurisdiction, "")
                    risk2 = self.clause_analyzer.analyze_clause(clause2_text, jurisdiction, "")
                    
                    if risk1.risk_score != risk2.risk_score:
                        risk_delta = risk2.risk_score - risk1.risk_score
                        change_type = "risk_increased" if risk_delta > 0 else "risk_decreased"
                        
                        risk_changes.append(RiskChange(
                            change_type=change_type,
                            clause_text=clause2_text[:300],
                            risk_score_delta=risk_delta,
                            old_risk_level=risk1.risk_level,
                            new_risk_level=risk2.risk_level,
                            risk_factors=risk2.issues,
                            recommendation=f"Risk changed from {risk1.risk_level} to {risk2.risk_level}"
                        ))
            
            elif alignment_type == "modified":
                # Analyze both versions
                risk1 = self.clause_analyzer.analyze_clause(clause1_text, jurisdiction, "")
                risk2 = self.clause_analyzer.analyze_clause(clause2_text, jurisdiction, "")
                
                risk_delta = risk2.risk_score - risk1.risk_score
                if risk_delta > 0.1:
                    change_type = "risk_increased"
                elif risk_delta < -0.1:
                    change_type = "risk_decreased"
                else:
                    change_type = "neutral"
                
                risk_changes.append(RiskChange(
                    change_type=change_type,
                    clause_text=clause2_text[:300],
                    risk_score_delta=risk_delta,
                    old_risk_level=risk1.risk_level,
                    new_risk_level=risk2.risk_level,
                    risk_factors=risk2.issues,
                    recommendation=self._generate_risk_recommendation(risk1, risk2)
                ))
            
            elif alignment_type == "added":
                # New clause - check if it introduces risk
                risk = self.clause_analyzer.analyze_clause(clause2_text, jurisdiction, "")
                if risk.risk_score > 0.3:
                    risk_changes.append(RiskChange(
                        change_type="risk_introduced",
                        clause_text=clause2_text[:300],
                        risk_score_delta=risk.risk_score,
                        old_risk_level=None,
                        new_risk_level=risk.risk_level,
                        risk_factors=risk.issues,
                        recommendation=f"New clause introduces {risk.risk_level} risk: {', '.join(risk.issues[:2])}"
                    ))
            
            elif alignment_type == "removed":
                # Removed clause - check if risk was reduced
                risk = self.clause_analyzer.analyze_clause(clause1_text, jurisdiction, "")
                if risk.risk_score > 0.3:
                    risk_changes.append(RiskChange(
                        change_type="risk_removed",
                        clause_text=clause1_text[:300],
                        risk_score_delta=-risk.risk_score,
                        old_risk_level=risk.risk_level,
                        new_risk_level=None,
                        risk_factors=risk.issues,
                        recommendation=f"Removed {risk.risk_level} risk clause"
                    ))
        
        # Sort by risk delta (highest risk increases first)
        risk_changes.sort(key=lambda x: x.risk_score_delta, reverse=True)
        
        return {
            "total_changes": len(risk_changes),
            "risk_increased": len([r for r in risk_changes if r.change_type == "risk_increased"]),
            "risk_decreased": len([r for r in risk_changes if r.change_type == "risk_decreased"]),
            "risk_introduced": len([r for r in risk_changes if r.change_type == "risk_introduced"]),
            "risk_removed": len([r for r in risk_changes if r.change_type == "risk_removed"]),
            "risk_changes": [self._risk_change_to_dict(r) for r in risk_changes]
        }
    
    def _generate_risk_recommendation(self, risk1, risk2) -> str:
        """Generate recommendation based on risk change"""
        if risk2.risk_score > risk1.risk_score:
            return f"Risk increased from {risk1.risk_level} to {risk2.risk_level}. Review changes carefully."
        elif risk2.risk_score < risk1.risk_score:
            return f"Risk decreased from {risk1.risk_level} to {risk2.risk_level}. Improvement noted."
        else:
            return "Risk level unchanged, but clause was modified."
    
    def _risk_change_to_dict(self, risk_change: RiskChange) -> Dict[str, Any]:
        """Convert RiskChange to dictionary"""
        return {
            "change_type": risk_change.change_type,
            "clause_text": risk_change.clause_text,
            "risk_score_delta": risk_change.risk_score_delta,
            "old_risk_level": risk_change.old_risk_level,
            "new_risk_level": risk_change.new_risk_level,
            "risk_factors": risk_change.risk_factors,
            "recommendation": risk_change.recommendation
        }

