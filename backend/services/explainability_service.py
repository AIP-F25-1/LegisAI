"""
Explainability Service
Provides consistent citation formatting, probability scores, and credibility scoring
"""

import logging
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Citation:
    """Formatted legal citation"""
    text: str
    type: str  # "case", "statute", "regulation", "treatise"
    credibility_score: float  # 0.0 to 1.0
    probability: float  # 0.0 to 1.0
    source: str
    metadata: Dict[str, Any]

@dataclass
class ExplainableResult:
    """Result with explainability metadata"""
    content: Any
    citations: List[Citation]
    confidence_score: float
    probability_scores: Dict[str, float]
    reasoning: str

class ExplainabilityService:
    """Service for providing explainability features"""
    
    def __init__(self):
        """Initialize explainability service"""
        # Citation patterns
        self.case_pattern = re.compile(
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+v\.\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)[,\s]+(\d+)\s+([A-Z]{2,})\s+(\d+)',
            re.IGNORECASE
        )
        self.statute_pattern = re.compile(
            r'([A-Z]{2,})\s+§\s+(\d+)',
            re.IGNORECASE
        )
        self.regulation_pattern = re.compile(
            r'(\d+)\s+CFR\s+§\s+(\d+\.\d+)',
            re.IGNORECASE
        )
    
    def format_citation(self, citation_text: str, citation_type: Optional[str] = None) -> Citation:
        """
        Format a citation with metadata
        
        Args:
            citation_text: Raw citation text
            citation_type: Type of citation (case, statute, regulation, treatise)
            
        Returns:
            Formatted Citation object
        """
        # Auto-detect type if not provided
        if not citation_type:
            if self.case_pattern.search(citation_text):
                citation_type = "case"
            elif self.statute_pattern.search(citation_text):
                citation_type = "statute"
            elif self.regulation_pattern.search(citation_text):
                citation_type = "regulation"
            else:
                citation_type = "treatise"
        
        # Calculate credibility score based on type and format
        credibility = self._calculate_credibility(citation_text, citation_type)
        
        # Extract metadata
        metadata = self._extract_metadata(citation_text, citation_type)
        
        return Citation(
            text=citation_text,
            type=citation_type,
            credibility_score=credibility,
            probability=0.85,  # Default probability
            source="",
            metadata=metadata
        )
    
    def _calculate_credibility(self, citation_text: str, citation_type: str) -> float:
        """
        Calculate credibility score for a citation
        
        Args:
            citation_text: Citation text
            citation_type: Type of citation
            
        Returns:
            Credibility score (0.0 to 1.0)
        """
        base_scores = {
            "case": 0.9,
            "statute": 0.95,
            "regulation": 0.92,
            "treatise": 0.75
        }
        
        base_score = base_scores.get(citation_type, 0.7)
        
        # Boost score if citation is well-formatted
        if self._is_well_formatted(citation_text, citation_type):
            base_score += 0.05
        
        # Boost score if citation includes year
        if re.search(r'\d{4}', citation_text):
            base_score += 0.03
        
        return min(1.0, base_score)
    
    def _is_well_formatted(self, citation_text: str, citation_type: str) -> bool:
        """Check if citation is well-formatted"""
        if citation_type == "case":
            return bool(self.case_pattern.search(citation_text))
        elif citation_type == "statute":
            return bool(self.statute_pattern.search(citation_text))
        elif citation_type == "regulation":
            return bool(self.regulation_pattern.search(citation_text))
        return True
    
    def _extract_metadata(self, citation_text: str, citation_type: str) -> Dict[str, Any]:
        """Extract metadata from citation"""
        metadata = {
            "type": citation_type,
            "raw_text": citation_text
        }
        
        if citation_type == "case":
            match = self.case_pattern.search(citation_text)
            if match:
                metadata["plaintiff"] = match.group(1)
                metadata["defendant"] = match.group(2)
                metadata["volume"] = match.group(3)
                metadata["reporter"] = match.group(4)
                metadata["page"] = match.group(5)
        
        elif citation_type == "statute":
            match = self.statute_pattern.search(citation_text)
            if match:
                metadata["code"] = match.group(1)
                metadata["section"] = match.group(2)
        
        elif citation_type == "regulation":
            match = self.regulation_pattern.search(citation_text)
            if match:
                metadata["title"] = match.group(1)
                metadata["section"] = match.group(2)
        
        return metadata
    
    def add_citations_to_result(
        self,
        result: Dict[str, Any],
        citations: List[str],
        probability: float = 0.85
    ) -> Dict[str, Any]:
        """
        Add formatted citations to a result
        
        Args:
            result: Result dictionary
            citations: List of citation strings
            probability: Probability score for the result
            
        Returns:
            Result with added citations and explainability metadata
        """
        formatted_citations = [
            self.format_citation(citation) for citation in citations
        ]
        
        # Update credibility based on citations
        if formatted_citations:
            avg_credibility = sum(c.credibility_score for c in formatted_citations) / len(formatted_citations)
        else:
            avg_credibility = 0.7
        
        result["citations"] = [
            {
                "text": c.text,
                "type": c.type,
                "credibility_score": c.credibility_score,
                "probability": c.probability,
                "metadata": c.metadata
            }
            for c in formatted_citations
        ]
        result["explainability"] = {
            "confidence_score": result.get("confidence_score", probability),
            "probability": probability,
            "credibility_score": avg_credibility,
            "citation_count": len(formatted_citations),
            "reasoning": f"Based on {len(formatted_citations)} legal sources with average credibility {avg_credibility:.2f}"
        }
        
        return result
    
    def calculate_probability_score(
        self,
        score: float,
        source_count: int,
        credibility: float
    ) -> float:
        """
        Calculate probability score from multiple factors
        
        Args:
            score: Base relevance/confidence score
            source_count: Number of supporting sources
            credibility: Average credibility of sources
            
        Returns:
            Probability score (0.0 to 1.0)
        """
        # Weighted combination
        probability = (
            score * 0.5 +  # Base score
            min(1.0, source_count / 10) * 0.3 +  # Source count (max at 10 sources)
            credibility * 0.2  # Credibility
        )
        
        return min(1.0, probability)
    
    def format_explainable_result(
        self,
        content: Any,
        citations: List[str],
        confidence: float,
        reasoning: str = ""
    ) -> ExplainableResult:
        """
        Create an explainable result with all metadata
        
        Args:
            content: Main content/result
            citations: List of citation strings
            confidence: Confidence score
            reasoning: Explanation of the result
            
        Returns:
            ExplainableResult object
        """
        formatted_citations = [
            self.format_citation(citation) for citation in citations
        ]
        
        avg_credibility = (
            sum(c.credibility_score for c in formatted_citations) / len(formatted_citations)
            if formatted_citations else 0.7
        )
        
        probability = self.calculate_probability_score(
            confidence,
            len(formatted_citations),
            avg_credibility
        )
        
        return ExplainableResult(
            content=content,
            citations=formatted_citations,
            confidence_score=confidence,
            probability_scores={
                "overall": probability,
                "relevance": confidence,
                "credibility": avg_credibility,
                "source_support": min(1.0, len(formatted_citations) / 10)
            },
            reasoning=reasoning or f"Based on {len(formatted_citations)} sources with {avg_credibility:.2f} average credibility"
        )

