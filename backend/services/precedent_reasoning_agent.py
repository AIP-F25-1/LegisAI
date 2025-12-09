"""
Precedent Reasoning Agent Service
Finds cases that support or weaken a position, and detects outdated precedents
"""

import logging
import asyncio
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CaseAlignment:
    """Case alignment analysis"""
    case_id: str
    case_name: str
    alignment_type: str  # "supporting", "weakening", "neutral"
    alignment_score: float  # 0.0 to 1.0
    reasoning: str
    key_factors: List[str]
    legal_principles: List[str]

@dataclass
class PrecedentStatus:
    """Status of a precedent"""
    case_id: str
    case_name: str
    status: str  # "active", "overruled", "distinguished", "limited"
    status_confidence: float  # 0.0 to 1.0
    reasoning: str
    overruling_cases: List[str]
    distinguishing_cases: List[str]
    limiting_cases: List[str]

class PrecedentReasoningAgent:
    """Analyzes case relationships and precedent status"""
    
    def __init__(self, hybrid_retriever=None, vector_store=None, ollama_client=None, ollama_model: str = "llama3.1:8b"):
        """
        Initialize precedent reasoning agent
        
        Args:
            hybrid_retriever: HybridRetriever instance for case search
            vector_store: VectorStore instance for semantic search
            ollama_client: Ollama client for AI analysis
            ollama_model: Model name to use
        """
        self.hybrid_retriever = hybrid_retriever
        self.vector_store = vector_store
        self.ollama_client = ollama_client
        self.ollama_model = ollama_model
        
        # Patterns for detecting precedent status indicators
        self.overruled_patterns = [
            r"overruled",
            r"overruling",
            r"explicitly overruled",
            r"no longer good law",
            r"superseded"
        ]
        
        self.distinguished_patterns = [
            r"distinguished",
            r"distinguishing",
            r"factually distinguishable",
            r"not applicable",
            r"different circumstances"
        ]
        
        self.limited_patterns = [
            r"limited",
            r"narrowed",
            r"restricted",
            r"confined to",
            r"only applies to"
        ]
    
    async def _generate_ai_analysis(self, prompt: str, max_tokens: int = 1500) -> str:
        """Generate AI analysis using Ollama"""
        if not self.ollama_client:
            return "LLM not available for analysis"
        
        try:
            # Check if async client
            if hasattr(self.ollama_client, 'generate') and asyncio.iscoroutinefunction(self.ollama_client.generate):
                response = await self.ollama_client.generate(
                    model=self.ollama_model,
                    prompt=prompt,
                    options={
                        'temperature': 0.3,
                        'top_p': 0.9,
                        'num_predict': max_tokens
                    }
                )
                if hasattr(response, 'response'):
                    return response.response
                elif isinstance(response, dict):
                    return response.get('response', '')
                else:
                    return str(response)
            else:
                # Sync client - run in executor
                loop = asyncio.get_event_loop()
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = loop.run_in_executor(
                        executor,
                        lambda: self.ollama_client.generate(
                            model=self.ollama_model,
                            prompt=prompt,
                            options={
                                'temperature': 0.3,
                                'top_p': 0.9,
                                'num_predict': max_tokens
                            }
                        )
                    )
                    response = await asyncio.wait_for(future, timeout=120.0)
                    if hasattr(response, 'response'):
                        return response.response
                    elif isinstance(response, dict):
                        return response.get('response', '')
                    else:
                        return str(response)
        except asyncio.TimeoutError:
            logger.warning("AI analysis timed out")
            return "Analysis timed out"
        except Exception as e:
            logger.error(f"Error generating analysis: {e}")
            return f"Error: {str(e)}"
    
    async def cross_case_alignment(
        self, 
        position: str, 
        position_type: str = "plaintiff",
        max_cases: int = 10
    ) -> Dict[str, Any]:
        """
        Find cases that support or weaken a given legal position
        
        Args:
            position: The legal position or argument to analyze
            position_type: "plaintiff", "defendant", or "neutral"
            max_cases: Maximum number of cases to return
            
        Returns:
            Dictionary with supporting, weakening, and neutral cases
        """
        logger.info(f"🔍 Finding cases that align with position: {position[:50]}...")
        
        if not self.hybrid_retriever and not self.vector_store:
            return {
                "error": "No search capability available",
                "supporting_cases": [],
                "weakening_cases": [],
                "neutral_cases": []
            }
        
        # Search for relevant cases
        try:
            if self.hybrid_retriever and self.hybrid_retriever.bm25_index:
                search_results = self.hybrid_retriever.search(
                    position,
                    k=max_cases * 2,
                    semantic_weight=0.7,
                    keyword_weight=0.3
                )
            elif self.vector_store:
                search_results = self.vector_store.search(position, k=max_cases * 2)
            else:
                search_results = []
            
            if not search_results:
                return {
                    "supporting_cases": [],
                    "weakening_cases": [],
                    "neutral_cases": [],
                    "message": "No relevant cases found"
                }
            
            # Analyze each case for alignment
            supporting_cases = []
            weakening_cases = []
            neutral_cases = []
            
            # Use AI to analyze alignment if available
            if self.ollama_client:
                for case in search_results[:max_cases]:
                    case_text = case.get('text', '')[:2000]  # Limit text length
                    case_name = case.get('metadata', {}).get('title', case.get('metadata', {}).get('case_name', 'Unknown Case'))
                    
                    alignment_prompt = f"""Analyze whether this case supports or weakens the following legal position:

POSITION ({position_type}): {position}

CASE: {case_name}
CASE TEXT: {case_text}

Determine:
1. ALIGNMENT: Does this case support, weaken, or is neutral to the position?
2. SCORE: Rate alignment from 0.0 (strongly weakens) to 1.0 (strongly supports)
3. REASONING: Why does this case support/weaken/neutral?
4. KEY FACTORS: List 2-3 key factors that determine alignment
5. LEGAL PRINCIPLES: List legal principles from this case relevant to the position

Format:
ALIGNMENT: [supporting/weakening/neutral]
SCORE: [0.0-1.0]
REASONING: [explanation]
KEY FACTORS:
- [factor 1]
- [factor 2]
LEGAL PRINCIPLES:
- [principle 1]
- [principle 2]"""
                    
                    analysis = await self._generate_ai_analysis(alignment_prompt, max_tokens=800)
                    alignment = self._parse_alignment(analysis, case, case_name)
                    
                    if alignment.alignment_type == "supporting":
                        supporting_cases.append(alignment)
                    elif alignment.alignment_type == "weakening":
                        weakening_cases.append(alignment)
                    else:
                        neutral_cases.append(alignment)
            else:
                # Fallback: Use similarity scores as proxy
                for case in search_results[:max_cases]:
                    score = case.get('score', case.get('combined_score', 0.5))
                    case_name = case.get('metadata', {}).get('title', 'Unknown Case')
                    
                    # Simple heuristic: high similarity = supporting, low = weakening
                    if score > 0.6:
                        alignment_type = "supporting"
                    elif score < 0.4:
                        alignment_type = "weakening"
                    else:
                        alignment_type = "neutral"
                    
                    alignment = CaseAlignment(
                        case_id=case.get('id', ''),
                        case_name=case_name,
                        alignment_type=alignment_type,
                        alignment_score=float(score),
                        reasoning=f"Based on similarity score: {score:.2f}",
                        key_factors=[],
                        legal_principles=[]
                    )
                    
                    if alignment_type == "supporting":
                        supporting_cases.append(alignment)
                    elif alignment_type == "weakening":
                        weakening_cases.append(alignment)
                    else:
                        neutral_cases.append(alignment)
            
            # Sort by alignment score
            supporting_cases.sort(key=lambda x: x.alignment_score, reverse=True)
            weakening_cases.sort(key=lambda x: x.alignment_score)
            neutral_cases.sort(key=lambda x: abs(x.alignment_score - 0.5))
            
            return {
                "position": position,
                "position_type": position_type,
                "supporting_cases": [self._alignment_to_dict(c) for c in supporting_cases[:max_cases]],
                "weakening_cases": [self._alignment_to_dict(c) for c in weakening_cases[:max_cases]],
                "neutral_cases": [self._alignment_to_dict(c) for c in neutral_cases[:max_cases]],
                "total_supporting": len(supporting_cases),
                "total_weakening": len(weakening_cases),
                "total_neutral": len(neutral_cases)
            }
            
        except Exception as e:
            logger.error(f"Error in cross-case alignment: {e}")
            return {
                "error": str(e),
                "supporting_cases": [],
                "weakening_cases": [],
                "neutral_cases": []
            }
    
    def _parse_alignment(self, text: str, case: Dict, case_name: str) -> CaseAlignment:
        """Parse alignment analysis from AI response"""
        alignment_type = "neutral"
        score = 0.5
        reasoning = ""
        key_factors = []
        legal_principles = []
        
        current_section = None
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if 'ALIGNMENT' in line.upper():
                if 'supporting' in line.lower():
                    alignment_type = "supporting"
                    score = 0.7
                elif 'weakening' in line.lower():
                    alignment_type = "weakening"
                    score = 0.3
                else:
                    alignment_type = "neutral"
                    score = 0.5
            elif 'SCORE' in line.upper():
                try:
                    score_str = re.search(r'[\d.]+', line)
                    if score_str:
                        score = float(score_str.group())
                        score = max(0.0, min(1.0, score))
                except:
                    pass
            elif 'REASONING' in line.upper():
                current_section = 'reasoning'
                if ':' in line:
                    reasoning = line.split(':', 1)[1].strip()
            elif 'KEY FACTOR' in line.upper():
                current_section = 'factors'
            elif 'LEGAL PRINCIPLE' in line.upper():
                current_section = 'principles'
            elif line.startswith('-') or line.startswith('•'):
                content = line[1:].strip()
                if current_section == 'factors':
                    key_factors.append(content)
                elif current_section == 'principles':
                    legal_principles.append(content)
            elif current_section == 'reasoning' and not reasoning:
                reasoning = line
        
        # Fallbacks
        if not reasoning:
            reasoning = f"Alignment analysis for {case_name}"
        if not key_factors:
            key_factors = ["Analysis based on case similarity"]
        if not legal_principles:
            legal_principles = ["Legal principles not extracted"]
        
        return CaseAlignment(
            case_id=case.get('id', ''),
            case_name=case_name,
            alignment_type=alignment_type,
            alignment_score=score,
            reasoning=reasoning,
            key_factors=key_factors[:5],
            legal_principles=legal_principles[:5]
        )
    
    def _alignment_to_dict(self, alignment: CaseAlignment) -> Dict[str, Any]:
        """Convert CaseAlignment to dictionary"""
        return {
            "case_id": alignment.case_id,
            "case_name": alignment.case_name,
            "alignment_type": alignment.alignment_type,
            "alignment_score": alignment.alignment_score,
            "reasoning": alignment.reasoning,
            "key_factors": alignment.key_factors,
            "legal_principles": alignment.legal_principles
        }
    
    async def detect_outdated_precedent(
        self,
        case_name: str,
        case_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Detect if a precedent is outdated (overruled, distinguished, or limited)
        
        Args:
            case_name: Name of the case to check
            case_text: Optional case text for analysis
            
        Returns:
            Dictionary with precedent status and related cases
        """
        logger.info(f"🔍 Checking precedent status for: {case_name}")
        
        # Search for cases that mention this case
        search_query = f"{case_name} overruled distinguished limited"
        
        related_cases = []
        
        try:
            if self.hybrid_retriever and self.hybrid_retriever.bm25_index:
                search_results = self.hybrid_retriever.search(
                    search_query,
                    k=20,
                    semantic_weight=0.6,
                    keyword_weight=0.4
                )
            elif self.vector_store:
                search_results = self.vector_store.search(search_query, k=20)
            else:
                search_results = []
            
            # Analyze search results for precedent status indicators
            overruling_cases = []
            distinguishing_cases = []
            limiting_cases = []
            
            for case in search_results:
                case_text_content = case.get('text', '')
                case_title = case.get('metadata', {}).get('title', 'Unknown')
                
                # Pattern matching for status indicators
                text_lower = case_text_content.lower()
                
                if any(re.search(pattern, text_lower) for pattern in self.overruled_patterns):
                    if case_name.lower() in text_lower:
                        overruling_cases.append({
                            "case_name": case_title,
                            "case_id": case.get('id', ''),
                            "evidence": self._extract_evidence(case_text_content, case_name, "overruled")
                        })
                
                if any(re.search(pattern, text_lower) for pattern in self.distinguished_patterns):
                    if case_name.lower() in text_lower:
                        distinguishing_cases.append({
                            "case_name": case_title,
                            "case_id": case.get('id', ''),
                            "evidence": self._extract_evidence(case_text_content, case_name, "distinguished")
                        })
                
                if any(re.search(pattern, text_lower) for pattern in self.limited_patterns):
                    if case_name.lower() in text_lower:
                        limiting_cases.append({
                            "case_name": case_title,
                            "case_id": case.get('id', ''),
                            "evidence": self._extract_evidence(case_text_content, case_name, "limited")
                        })
            
            # Determine overall status
            status = "active"
            confidence = 0.5
            reasoning = f"No evidence found that {case_name} has been overruled, distinguished, or limited."
            
            if overruling_cases:
                status = "overruled"
                confidence = 0.9
                reasoning = f"{case_name} appears to have been overruled by {len(overruling_cases)} case(s)."
            elif distinguishing_cases:
                status = "distinguished"
                confidence = 0.7
                reasoning = f"{case_name} has been distinguished in {len(distinguishing_cases)} case(s)."
            elif limiting_cases:
                status = "limited"
                confidence = 0.6
                reasoning = f"{case_name} has been limited in scope by {len(limiting_cases)} case(s)."
            
            # Use AI for deeper analysis if available
            if self.ollama_client and case_text:
                ai_prompt = f"""Analyze the precedent status of this case:

CASE NAME: {case_name}
CASE TEXT: {case_text[:2000]}

RELATED CASES FOUND:
- Overruling: {len(overruling_cases)} cases
- Distinguishing: {len(distinguishing_cases)} cases  
- Limiting: {len(limiting_cases)} cases

Determine:
1. STATUS: Is this case active, overruled, distinguished, or limited?
2. CONFIDENCE: How confident are you (0.0-1.0)?
3. REASONING: Explain the precedent status
4. RECOMMENDATION: Should this case still be cited?

Format:
STATUS: [active/overruled/distinguished/limited]
CONFIDENCE: [0.0-1.0]
REASONING: [detailed explanation]
RECOMMENDATION: [should cite/should not cite/use with caution]"""
                
                ai_analysis = await self._generate_ai_analysis(ai_prompt, max_tokens=1000)
                ai_status = self._parse_precedent_status(ai_analysis, case_name)
                
                # Use AI analysis if more confident
                if ai_status.status_confidence > confidence:
                    status = ai_status.status
                    confidence = ai_status.status_confidence
                    reasoning = ai_status.reasoning
            
            return {
                "case_name": case_name,
                "status": status,
                "status_confidence": confidence,
                "reasoning": reasoning,
                "overruling_cases": overruling_cases[:10],
                "distinguishing_cases": distinguishing_cases[:10],
                "limiting_cases": limiting_cases[:10],
                "total_overruling": len(overruling_cases),
                "total_distinguishing": len(distinguishing_cases),
                "total_limiting": len(limiting_cases)
            }
            
        except Exception as e:
            logger.error(f"Error detecting outdated precedent: {e}")
            return {
                "case_name": case_name,
                "status": "unknown",
                "status_confidence": 0.0,
                "reasoning": f"Error analyzing precedent: {str(e)}",
                "overruling_cases": [],
                "distinguishing_cases": [],
                "limiting_cases": []
            }
    
    def _extract_evidence(self, text: str, case_name: str, status_type: str) -> str:
        """Extract evidence sentence mentioning the case and status"""
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            if case_name.lower() in sentence.lower() and status_type in sentence.lower():
                return sentence.strip()[:200]
        return f"Found reference to {case_name} being {status_type}"
    
    def _parse_precedent_status(self, text: str, case_name: str) -> PrecedentStatus:
        """Parse precedent status from AI response"""
        status = "active"
        confidence = 0.5
        reasoning = ""
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if 'STATUS' in line.upper():
                if 'overruled' in line.lower():
                    status = "overruled"
                elif 'distinguished' in line.lower():
                    status = "distinguished"
                elif 'limited' in line.lower():
                    status = "limited"
                else:
                    status = "active"
            elif 'CONFIDENCE' in line.upper():
                try:
                    score_str = re.search(r'[\d.]+', line)
                    if score_str:
                        confidence = float(score_str.group())
                        confidence = max(0.0, min(1.0, confidence))
                except:
                    pass
            elif 'REASONING' in line.upper():
                if ':' in line:
                    reasoning = line.split(':', 1)[1].strip()
        
        if not reasoning:
            reasoning = f"Status analysis for {case_name}"
        
        return PrecedentStatus(
            case_id="",
            case_name=case_name,
            status=status,
            status_confidence=confidence,
            reasoning=reasoning,
            overruling_cases=[],
            distinguishing_cases=[],
            limiting_cases=[]
        )

