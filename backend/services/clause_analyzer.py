"""
Clause Analysis and Risk Detection Service
Detects risky, unenforceable, or problematic clauses in legal documents
"""

import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ClauseRisk:
    """Risk assessment for a clause"""
    clause_text: str
    risk_level: str  # "low", "medium", "high", "critical"
    risk_score: float  # 0.0 to 1.0
    risk_type: str  # "unenforceable", "risky", "ambiguous", "unfair", "non-compliant"
    issues: List[str]
    recommendations: List[str]
    jurisdiction: str
    legal_basis: Optional[str] = None

class ClauseAnalyzer:
    """Analyzes clauses for risks and compliance issues"""
    
    def __init__(self):
        """Initialize clause analyzer with risk patterns"""
        self.risk_patterns = self._load_risk_patterns()
        self.jurisdiction_rules = self._load_jurisdiction_rules()
    
    def _load_risk_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load risk detection patterns"""
        return {
            "unenforceable": [
                {
                    "pattern": r"(?:waive|waiver|waiving).*gross negligence|gross negligence.*(?:waive|waiver|waiving)",
                    "risk": "high",
                    "issue": "Waivers of gross negligence are often unenforceable",
                    "recommendation": "Review jurisdiction-specific case law on gross negligence waivers"
                },
                {
                    "pattern": r"(?:waive|waiver|waiving).*willful misconduct|willful misconduct.*(?:waive|waiver|waiving)",
                    "risk": "high",
                    "issue": "Waivers of willful misconduct are typically unenforceable",
                    "recommendation": "Remove or limit waiver of willful misconduct"
                },
                {
                    "pattern": r"gross negligence",
                    "risk": "high",
                    "issue": "Gross negligence clauses may be unenforceable",
                    "recommendation": "Review jurisdiction-specific case law on gross negligence"
                },
                {
                    "pattern": r"willful misconduct",
                    "risk": "high",
                    "issue": "Willful misconduct clauses may be unenforceable",
                    "recommendation": "Review jurisdiction-specific case law on willful misconduct"
                },
                {
                    "pattern": r"unconscionable|unconscionably",
                    "risk": "medium",
                    "issue": "Unconscionable terms may be unenforceable",
                    "recommendation": "Ensure terms are reasonable and not one-sided"
                },
                {
                    "pattern": r"penalty.*damages|liquidated damages.*penalty",
                    "risk": "medium",
                    "issue": "Penalty clauses (vs. liquidated damages) may be unenforceable",
                    "recommendation": "Ensure damages are reasonable estimates, not penalties"
                }
            ],
            "risky": [
                {
                    "pattern": r"unlimited liability|liability.*unlimited",
                    "risk": "high",
                    "issue": "Unlimited liability exposes party to significant risk",
                    "recommendation": "Consider liability caps or insurance requirements"
                },
                {
                    "pattern": r"indemnif.*all claims|indemnif.*without limitation|indemnif.*any claims",
                    "risk": "high",
                    "issue": "Broad indemnification clauses can be very risky",
                    "recommendation": "Limit indemnification to third-party claims arising from breach"
                },
                {
                    "pattern": r"without limitation",
                    "risk": "medium",
                    "issue": "Clauses without limitation can be overly broad",
                    "recommendation": "Consider adding reasonable limitations"
                },
                {
                    "pattern": r"assignment.*without consent|assign.*freely",
                    "risk": "medium",
                    "issue": "Unrestricted assignment may transfer obligations unexpectedly",
                    "recommendation": "Require consent for assignment or limit to affiliates"
                },
                {
                    "pattern": r"termination.*without cause|terminate.*at will",
                    "risk": "medium",
                    "issue": "Termination without cause may lack protection",
                    "recommendation": "Consider notice periods and termination fees"
                }
            ],
            "ambiguous": [
                {
                    "pattern": r"reasonable|best efforts|commercially reasonable",
                    "risk": "medium",
                    "issue": "Vague terms like 'reasonable' may lead to disputes",
                    "recommendation": "Define specific standards or metrics where possible"
                },
                {
                    "pattern": r"as soon as practicable|in a timely manner",
                    "risk": "medium",
                    "issue": "Ambiguous timeframes can cause confusion",
                    "recommendation": "Specify exact timeframes or deadlines"
                },
                {
                    "pattern": r"\b(maybe|perhaps|probably|might|sort of|kinda|whatever|whenever|somehow|if.*feel|depending on.*mood)\b",
                    "risk": "high",
                    "issue": "Highly ambiguous and informal language creates significant legal uncertainty",
                    "recommendation": "Use precise, legally binding language with clear terms and conditions"
                },
                {
                    "pattern": r"(?:payment|amount|price|fee).*(?:fair|whatever|maybe|probably|not fixed|not specified)",
                    "risk": "high",
                    "issue": "Unspecified payment terms create financial risk and disputes",
                    "recommendation": "Specify exact payment amounts, schedules, and methods"
                },
                {
                    "pattern": r"(?:deadline|timeframe|duration).*(?:maybe|whenever|no.*deadline|not specified|undefined)",
                    "risk": "high",
                    "issue": "Lack of clear deadlines creates project management and legal risks",
                    "recommendation": "Specify clear start dates, milestones, and completion deadlines"
                },
                {
                    "pattern": r"(?:ownership|belongs|property).*(?:unless.*says|maybe|not clear|ambiguous)",
                    "risk": "high",
                    "issue": "Unclear ownership rights can lead to intellectual property disputes",
                    "recommendation": "Clearly define ownership, licensing, and usage rights for all deliverables"
                },
                {
                    "pattern": r"(?:terminate|end|cancel).*(?:whenever|bored|stop replying|no notice|not required)",
                    "risk": "high",
                    "issue": "Lack of proper termination procedures creates legal and business risks",
                    "recommendation": "Specify termination conditions, notice periods, and post-termination obligations"
                },
                {
                    "pattern": r"(?:confidential|private).*(?:kinda|maybe|leak.*okay|mistakes happen)",
                    "risk": "high",
                    "issue": "Weak confidentiality provisions expose sensitive information to risk",
                    "recommendation": "Include strong confidentiality clauses with clear penalties for breaches"
                },
                {
                    "pattern": r"(?:signature|sign).*(?:or not|maybe|thumbs.*up|emoji)",
                    "risk": "medium",
                    "issue": "Informal signature requirements may invalidate the contract",
                    "recommendation": "Require proper written signatures with dates for legal validity"
                },
                {
                    "pattern": r"(?:work|deliverables|scope).*(?:whatever|maybe|figure.*out.*later|not specified)",
                    "risk": "high",
                    "issue": "Unclear scope of work creates performance and payment disputes",
                    "recommendation": "Define specific deliverables, milestones, and acceptance criteria"
                },
                {
                    "pattern": r"(?:dispute|problem|sue).*(?:maybe|probably.*fine|no.*court|whoever.*files)",
                    "risk": "high",
                    "issue": "Lack of dispute resolution mechanism creates legal uncertainty",
                    "recommendation": "Specify dispute resolution procedures, governing law, and jurisdiction"
                }
            ],
            "non_compliant": [
                {
                    "pattern": r"non-compete.*perpetual|non-compete.*unlimited",
                    "risk": "high",
                    "issue": "Overly broad non-compete clauses may violate labor laws",
                    "recommendation": "Limit non-compete to reasonable duration and geographic scope"
                },
                {
                    "pattern": r"data.*without consent|process.*personal data.*freely|personal data.*without|data.*no consent",
                    "risk": "high",
                    "issue": "May violate GDPR/privacy regulations",
                    "recommendation": "Ensure proper consent mechanisms and data protection measures"
                },
                {
                    "pattern": r"personal data.*without consent|personal information.*without consent|process.*personal data.*freely",
                    "risk": "high",
                    "issue": "Personal data processing without consent may violate GDPR",
                    "recommendation": "Ensure explicit consent mechanisms for data processing"
                }
            ]
        }
    
    def _load_jurisdiction_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load jurisdiction-specific rules"""
        return {
            "US": {
                "unenforceable_patterns": [
                    r"(?:waive|waiver|waiving).*gross negligence|gross negligence.*(?:waive|waiver|waiving)",
                    r"gross negligence",
                    r"penalty.*liquidated damages|liquidated damages.*penalty"
                ],
                "risk_factors": {
                    "unconscionability": 0.7,
                    "public_policy": 0.8
                }
            },
            "EU": {
                "unenforceable_patterns": [
                    r"unfair.*consumer|consumer.*unfair",
                    r"unfair.*commercial"
                ],
                "risk_factors": {
                    "gdpr_violation": 0.9,
                    "unfair_terms": 0.8
                }
            },
            "UK": {
                "unenforceable_patterns": [
                    r"penalty.*damages",
                    r"unfair.*consumer"
                ],
                "risk_factors": {
                    "unfair_terms": 0.8,
                    "consumer_protection": 0.7
                }
            }
        }
    
    def extract_clauses(self, document_text: str) -> List[Dict[str, Any]]:
        """
        Extract individual clauses from document text
        
        Args:
            document_text: Full document text
            
        Returns:
            List of clauses with metadata
        """
        clauses = []
        
        # Split by common clause markers
        clause_patterns = [
            r"(?:^|\n)\s*(?:Section|Clause|Article)\s+\d+[\.:]?\s*[^\n]+",  # Section 1: ...
            r"(?:^|\n)\s*\d+\.\s+[A-Z][^\n]+",  # 1. Clause title
            r"(?:^|\n)\s*[A-Z][A-Z\s]{10,}:"  # ALL CAPS HEADER:
        ]
        
        # Try paragraph-based splitting first (more meaningful than sentences)
        paragraphs = [p.strip() for p in document_text.split('\n\n') if p.strip() and len(p.strip()) > 30]
        
        if paragraphs:
            for i, para in enumerate(paragraphs[:30]):  # Limit to 30 paragraphs
                clauses.append({
                    "id": f"clause_{i}",
                    "text": para,
                    "type": "paragraph"
                })
        
        # If no paragraphs or too few, try sentence-based with grouping
        if len(clauses) < 3:
            sentences = re.split(r'[.!?]\s+', document_text)
            current_clause = ""
            clause_num = 0
            sentence_count = 0
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence or len(sentence) < 10:
                    continue
                
                sentence_count += 1
                current_clause += " " + sentence if current_clause else sentence
                
                # Check if this looks like a clause header
                if re.match(r'^(?:Section|Clause|Article|Part)\s+\d+', sentence, re.IGNORECASE):
                    if current_clause and len(current_clause.strip()) > 30:
                        clauses.append({
                            "id": f"clause_{clause_num}",
                            "text": current_clause.strip(),
                            "type": "general"
                        })
                        clause_num += 1
                    current_clause = sentence
                    sentence_count = 0
                # Group sentences into clauses (3-5 sentences per clause)
                elif sentence_count >= 3 and len(current_clause) > 100:
                    clauses.append({
                        "id": f"clause_{clause_num}",
                        "text": current_clause.strip(),
                        "type": "grouped"
                    })
                    clause_num += 1
                    current_clause = ""
                    sentence_count = 0
            
            # Add last clause
            if current_clause and len(current_clause.strip()) > 30:
                clauses.append({
                    "id": f"clause_{clause_num}",
                    "text": current_clause.strip(),
                    "type": "general"
                })
        
        # If no clauses found, split into paragraphs
        if not clauses:
            paragraphs = [p.strip() for p in document_text.split('\n\n') if p.strip()]
            for i, para in enumerate(paragraphs[:20]):  # Limit to first 20 paragraphs
                if len(para) > 50:  # Only substantial paragraphs
                    clauses.append({
                        "id": f"clause_{len(clauses)}",  # Use len(clauses) to avoid duplicates
                        "text": para,
                        "type": "paragraph"
                    })
        
        # Remove duplicate clauses (same text)
        seen_texts = set()
        unique_clauses = []
        for clause in clauses:
            text_key = clause["text"].strip()[:100]  # Use first 100 chars as key
            if text_key not in seen_texts:
                seen_texts.add(text_key)
                unique_clauses.append(clause)
        
        return unique_clauses
    
    def analyze_clause(
        self, 
        clause_text: str, 
        jurisdiction: str = "US",
        document_context: Optional[str] = None
    ) -> ClauseRisk:
        """
        Analyze a single clause for risks
        
        Args:
            clause_text: The clause text to analyze
            jurisdiction: Jurisdiction code (US, EU, UK, etc.)
            document_context: Optional full document context
            
        Returns:
            ClauseRisk object with analysis
        """
        issues = []
        recommendations = []
        risk_scores = []
        risk_types = []
        
        clause_lower = clause_text.lower()
        
        # Check all risk categories
        for category, patterns in self.risk_patterns.items():
            for pattern_info in patterns:
                if re.search(pattern_info["pattern"], clause_lower, re.IGNORECASE):
                    issues.append(pattern_info["issue"])
                    recommendations.append(pattern_info["recommendation"])
                    
                    # Map risk level to score
                    risk_level_map = {
                        "low": 0.3,
                        "medium": 0.6,
                        "high": 0.8,
                        "critical": 0.95
                    }
                    risk_scores.append(risk_level_map.get(pattern_info["risk"], 0.5))
                    risk_types.append(category)
        
        # Check jurisdiction-specific rules
        if jurisdiction in self.jurisdiction_rules:
            rules = self.jurisdiction_rules[jurisdiction]
            for pattern in rules.get("unenforceable_patterns", []):
                if re.search(pattern, clause_lower, re.IGNORECASE):
                    issues.append(f"May violate {jurisdiction} law")
                    recommendations.append(f"Review with {jurisdiction} legal counsel")
                    risk_scores.append(0.85)
                    risk_types.append("non_compliant")
        
        # Calculate overall risk
        if risk_scores:
            max_risk = max(risk_scores)
            avg_risk = sum(risk_scores) / len(risk_scores)
            overall_risk = max(max_risk, avg_risk * 1.2)  # Weight towards highest risk
        else:
            overall_risk = 0.1  # Low risk if no issues found
        
        # Determine risk level
        if overall_risk >= 0.8:
            risk_level = "critical"
        elif overall_risk >= 0.6:
            risk_level = "high"
        elif overall_risk >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Primary risk type
        primary_risk_type = max(set(risk_types), key=risk_types.count) if risk_types else "none"
        
        return ClauseRisk(
            clause_text=clause_text[:200] + "..." if len(clause_text) > 200 else clause_text,
            risk_level=risk_level,
            risk_score=min(overall_risk, 1.0),
            risk_type=primary_risk_type,
            issues=issues[:5],  # Limit to top 5 issues
            recommendations=recommendations[:5],  # Limit to top 5 recommendations
            jurisdiction=jurisdiction,
            legal_basis=f"{jurisdiction} case law and regulations"
        )
    
    def analyze_document(
        self, 
        document_text: str, 
        jurisdiction: str = "US"
    ) -> Dict[str, Any]:
        """
        Analyze entire document for clause-level risks
        
        Args:
            document_text: Full document text
            jurisdiction: Jurisdiction code
            
        Returns:
            Dictionary with analysis results
        """
        clauses = self.extract_clauses(document_text)
        
        clause_risks = []
        total_risk_score = 0.0
        high_risk_count = 0
        
        for clause in clauses:
            risk = self.analyze_clause(clause["text"], jurisdiction, document_text)
            clause_risks.append({
                "clause_id": clause["id"],
                "clause_text": clause["text"][:150] + "..." if len(clause["text"]) > 150 else clause["text"],
                "risk_level": risk.risk_level,
                "risk_score": risk.risk_score,
                "risk_type": risk.risk_type,
                "issues": risk.issues,
                "recommendations": risk.recommendations
            })
            
            total_risk_score += risk.risk_score
            if risk.risk_level in ["high", "critical"]:
                high_risk_count += 1
        
        # Calculate document-level risk
        avg_risk = total_risk_score / len(clauses) if clauses else 0.0
        
        # Count risk levels
        critical_count = len([r for r in clause_risks if r["risk_level"] == "critical"])
        high_count = len([r for r in clause_risks if r["risk_level"] == "high"])
        medium_count = len([r for r in clause_risks if r["risk_level"] == "medium"])
        low_count = len([r for r in clause_risks if r["risk_level"] == "low"])
        
        # Determine document risk level based on:
        # 1. Highest individual clause risk (if any critical/high, document should reflect that)
        # 2. Average risk score (for overall assessment)
        # 3. Number of high-risk clauses (if many, elevate document level)
        
        # Determine document risk level based on:
        # 1. Highest individual clause risk (if any critical/high, document should reflect that)
        # 2. Average risk score (for overall assessment)
        # 3. Number of high-risk clauses (if many, elevate document level)
        # 
        # IMPORTANT: Document level should reflect the highest risk present, not just average
        # If all clauses are low-risk (10%), document should be LOW, not HIGH
        
        if critical_count > 0:
            # At least one critical clause = critical document
            document_risk_level = "critical"
        elif high_count > 0:
            # At least one high-risk clause = high document
            document_risk_level = "high"
        elif medium_count > 0:
            # At least one medium-risk clause = medium document
            document_risk_level = "medium"
        elif avg_risk >= 0.5:
            # High average risk (even if individual clauses are low) = medium document
            document_risk_level = "medium"
        elif avg_risk >= 0.3:
            # Medium average risk = medium document
            document_risk_level = "medium"
        else:
            # Low average and no risky clauses = low document
            document_risk_level = "low"
        
        return {
            "total_clauses": len(clauses),
            "high_risk_clauses": high_risk_count,
            "document_risk_level": document_risk_level,
            "average_risk_score": avg_risk,
            "clause_risks": clause_risks,
            "jurisdiction": jurisdiction,
            "summary": {
                "document_risk_level": document_risk_level,  # Also include in summary for frontend
                "average_risk_score": avg_risk,  # Also include in summary for frontend
                "critical_risks": critical_count,
                "high_risks": high_count,
                "medium_risks": medium_count,
                "low_risks": low_count
            }
        }
