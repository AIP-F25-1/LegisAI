"""
Summarization Agent Service
Extracts headnotes, ratio decidendi, obiter dicta, and generates contrastive summaries
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Headnote:
    """Headnote extracted from case"""
    summary: str
    key_points: List[str]
    legal_issues: List[str]
    holding: str

@dataclass
class ContrastiveSummary:
    """Contrastive summary showing both perspectives"""
    pro_plaintiff: Dict[str, Any]
    pro_defendant: Dict[str, Any]
    neutral_analysis: str

class SummarizationAgent:
    """Extracts legal document summaries and generates contrastive analyses"""
    
    def __init__(self, ollama_client=None, ollama_model: str = "llama3.1:8b"):
        """
        Initialize summarization agent
        
        Args:
            ollama_client: Ollama client instance (async or sync)
            ollama_model: Model name to use
        """
        self.ollama_client = ollama_client
        self.ollama_model = ollama_model
        self.use_async = hasattr(ollama_client, 'generate') if ollama_client else False
    
    async def _generate_ai_summary(self, prompt: str, max_tokens: int = 1500) -> str:
        """Generate AI summary using Ollama"""
        if not self.ollama_client:
            return "LLM not available for summarization"
        
        try:
            # Check if async client
            if hasattr(self.ollama_client, 'generate') and asyncio.iscoroutinefunction(self.ollama_client.generate):
                # Async client
                response = await self.ollama_client.generate(
                    model=self.ollama_model,
                    prompt=prompt,
                    options={
                        'temperature': 0.3,  # Lower temperature for more factual summaries
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
            logger.warning("Summarization timed out")
            return "Summarization timed out"
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Error: {str(e)}"
    
    async def extract_headnotes(self, case_text: str, case_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract headnotes from case text
        
        Args:
            case_text: Full text of the case
            case_name: Optional case name for context
            
        Returns:
            Dictionary with headnote, key points, legal issues, and holding
        """
        logger.info("📝 Extracting headnotes from case text...")
        
        case_context = f"Case: {case_name}\n\n" if case_name else ""
        prompt = f"""You are a legal expert extracting headnotes from a court case. Analyze the following case text and extract:

1. HEADNOTE SUMMARY: A concise 2-3 sentence summary of the case
2. KEY POINTS: List 3-5 key legal points or principles established
3. LEGAL ISSUES: List the main legal issues addressed
4. HOLDING: The court's decision and reasoning

{case_context}Case Text:
{case_text[:4000]}  # Limit to avoid token limits

Format your response as:
HEADNOTE: [summary]
KEY POINTS:
- [point 1]
- [point 2]
...
LEGAL ISSUES:
- [issue 1]
- [issue 2]
...
HOLDING: [court's decision and reasoning]"""

        summary_text = await self._generate_ai_summary(prompt, max_tokens=1000)
        
        # Parse the response
        headnote = self._parse_headnote(summary_text)
        
        return {
            "headnote": headnote.summary,
            "key_points": headnote.key_points,
            "legal_issues": headnote.legal_issues,
            "holding": headnote.holding,
            "raw_response": summary_text
        }
    
    def _parse_headnote(self, text: str) -> Headnote:
        """Parse headnote from AI response"""
        lines = text.split('\n')
        headnote = ""
        key_points = []
        legal_issues = []
        holding = ""
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.upper().startswith('HEADNOTE'):
                current_section = 'headnote'
                headnote = line.split(':', 1)[1].strip() if ':' in line else line
            elif line.upper().startswith('KEY POINT'):
                current_section = 'key_points'
                if ':' in line:
                    key_points.append(line.split(':', 1)[1].strip())
            elif line.upper().startswith('LEGAL ISSUE'):
                current_section = 'legal_issues'
                if ':' in line:
                    legal_issues.append(line.split(':', 1)[1].strip())
            elif line.upper().startswith('HOLDING'):
                current_section = 'holding'
                holding = line.split(':', 1)[1].strip() if ':' in line else line
            elif line.startswith('-') or line.startswith('•'):
                content = line[1:].strip()
                if current_section == 'key_points':
                    key_points.append(content)
                elif current_section == 'legal_issues':
                    legal_issues.append(content)
            elif current_section == 'headnote' and not headnote:
                headnote = line
            elif current_section == 'holding' and not holding:
                holding = line
        
        # Fallback if parsing failed
        if not headnote:
            headnote = text[:200] if text else "Unable to extract headnote"
        if not key_points:
            key_points = ["Key points not extracted"]
        if not legal_issues:
            legal_issues = ["Legal issues not extracted"]
        if not holding:
            holding = "Holding not extracted"
        
        return Headnote(
            summary=headnote,
            key_points=key_points[:5],  # Limit to 5
            legal_issues=legal_issues[:5],
            holding=holding
        )
    
    async def extract_ratio_decidendi(self, case_text: str, case_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract ratio decidendi (the legal reasoning/principle) from case text
        
        Args:
            case_text: Full text of the case
            case_name: Optional case name for context
            
        Returns:
            Dictionary with ratio decidendi and supporting details
        """
        logger.info("⚖️ Extracting ratio decidendi from case text...")
        
        case_context = f"Case: {case_name}\n\n" if case_name else ""
        prompt = f"""You are a legal expert extracting the ratio decidendi (the legal principle or reasoning) from a court case.

Ratio decidendi is the binding legal principle that forms the basis of the court's decision. It is distinct from obiter dicta (incidental remarks).

Analyze the following case text and extract:

1. RATIO DECIDENDI: The core legal principle or rule established by this case
2. REASONING: The court's legal reasoning that led to this principle
3. APPLICATION: How this principle applies to the facts of the case
4. PRECEDENT VALUE: What future cases this principle will bind

{case_context}Case Text:
{case_text[:4000]}

Format your response as:
RATIO DECIDENDI: [the core legal principle]
REASONING: [court's legal reasoning]
APPLICATION: [how it applies to facts]
PRECEDENT VALUE: [binding effect on future cases]"""

        summary_text = await self._generate_ai_summary(prompt, max_tokens=1200)
        
        # Parse the response
        ratio = self._parse_ratio_decidendi(summary_text)
        
        return {
            "ratio_decidendi": ratio.get("ratio", ""),
            "reasoning": ratio.get("reasoning", ""),
            "application": ratio.get("application", ""),
            "precedent_value": ratio.get("precedent_value", ""),
            "raw_response": summary_text
        }
    
    def _parse_ratio_decidendi(self, text: str) -> Dict[str, str]:
        """Parse ratio decidendi from AI response"""
        result = {
            "ratio": "",
            "reasoning": "",
            "application": "",
            "precedent_value": ""
        }
        
        current_section = None
        current_text = []
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                if current_section and current_text:
                    result[current_section] = ' '.join(current_text)
                    current_text = []
                continue
            
            if 'RATIO DECIDENDI' in line.upper():
                current_section = 'ratio'
                if ':' in line:
                    current_text = [line.split(':', 1)[1].strip()]
            elif 'REASONING' in line.upper() and 'APPLICATION' not in line.upper():
                if current_section and current_text:
                    result[current_section] = ' '.join(current_text)
                current_section = 'reasoning'
                current_text = [line.split(':', 1)[1].strip()] if ':' in line else []
            elif 'APPLICATION' in line.upper():
                if current_section and current_text:
                    result[current_section] = ' '.join(current_text)
                current_section = 'application'
                current_text = [line.split(':', 1)[1].strip()] if ':' in line else []
            elif 'PRECEDENT VALUE' in line.upper() or 'PRECEDENT' in line.upper():
                if current_section and current_text:
                    result[current_section] = ' '.join(current_text)
                current_section = 'precedent_value'
                current_text = [line.split(':', 1)[1].strip()] if ':' in line else []
            elif current_section:
                current_text.append(line)
        
        # Save last section
        if current_section and current_text:
            result[current_section] = ' '.join(current_text)
        
        # Fallbacks
        if not result["ratio"]:
            result["ratio"] = text[:300] if text else "Unable to extract ratio decidendi"
        
        return result
    
    async def extract_obiter_dicta(self, case_text: str, case_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract obiter dicta (incidental remarks) from case text
        
        Args:
            case_text: Full text of the case
            case_name: Optional case name for context
            
        Returns:
            Dictionary with obiter dicta and analysis
        """
        logger.info("💬 Extracting obiter dicta from case text...")
        
        case_context = f"Case: {case_name}\n\n" if case_name else ""
        prompt = f"""You are a legal expert identifying obiter dicta (incidental remarks) in a court case.

Obiter dicta are statements made by the court that are not essential to the decision and do not form binding precedent. They are often observations, opinions, or hypothetical scenarios.

Analyze the following case text and identify:

1. OBITER DICTA: List any statements that are not part of the core reasoning
2. NATURE: Explain why each is obiter (not binding)
3. POTENTIAL INFLUENCE: How these remarks might influence future cases (even if not binding)

{case_context}Case Text:
{case_text[:4000]}

Format your response as:
OBITER DICTA:
1. [statement 1]
   Nature: [why it's obiter]
   Influence: [potential impact]

2. [statement 2]
   Nature: [why it's obiter]
   Influence: [potential impact]"""

        summary_text = await self._generate_ai_summary(prompt, max_tokens=1500)
        
        # Parse the response
        obiter_list = self._parse_obiter_dicta(summary_text)
        
        return {
            "obiter_dicta": obiter_list,
            "count": len(obiter_list),
            "raw_response": summary_text
        }
    
    def _parse_obiter_dicta(self, text: str) -> List[Dict[str, str]]:
        """Parse obiter dicta from AI response"""
        obiter_list = []
        current_item = {}
        current_field = None
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                if current_item:
                    obiter_list.append(current_item)
                    current_item = {}
                continue
            
            # Check for numbered items
            if line[0].isdigit() and ('.' in line[:3] or ')' in line[:3]):
                if current_item:
                    obiter_list.append(current_item)
                current_item = {"statement": "", "nature": "", "influence": ""}
                # Extract statement
                parts = line.split('.', 1) if '.' in line[:3] else line.split(')', 1)
                if len(parts) > 1:
                    current_item["statement"] = parts[1].strip()
                current_field = "statement"
            elif 'NATURE' in line.upper() or 'Nature' in line:
                current_field = "nature"
                if ':' in line:
                    current_item["nature"] = line.split(':', 1)[1].strip()
            elif 'INFLUENCE' in line.upper() or 'Influence' in line:
                current_field = "influence"
                if ':' in line:
                    current_item["influence"] = line.split(':', 1)[1].strip()
            elif current_field and current_item:
                if current_item[current_field]:
                    current_item[current_field] += " " + line
                else:
                    current_item[current_field] = line
        
        if current_item:
            obiter_list.append(current_item)
        
        # Fallback
        if not obiter_list:
            obiter_list = [{
                "statement": text[:200] if text else "Unable to extract obiter dicta",
                "nature": "Not identified",
                "influence": "Unknown"
            }]
        
        return obiter_list[:10]  # Limit to 10 items
    
    async def contrastive_summary(self, case_text: str, case_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate contrastive summary showing pro-plaintiff vs pro-defendant perspectives
        
        Args:
            case_text: Full text of the case
            case_name: Optional case name for context
            
        Returns:
            Dictionary with pro-plaintiff, pro-defendant, and neutral analysis
        """
        logger.info("⚖️ Generating contrastive summary (pro-plaintiff vs pro-defendant)...")
        
        case_context = f"Case: {case_name}\n\n" if case_name else ""
        prompt = f"""You are a legal expert analyzing a court case from multiple perspectives.

Analyze the following case and provide:

1. PRO-PLAINTIFF ARGUMENTS: Arguments and evidence that support the plaintiff's position
   - Key facts favoring plaintiff
   - Legal principles supporting plaintiff
   - Strengths of plaintiff's case
   
2. PRO-DEFENDANT ARGUMENTS: Arguments and evidence that support the defendant's position
   - Key facts favoring defendant
   - Legal principles supporting defendant
   - Strengths of defendant's case

3. NEUTRAL ANALYSIS: Objective assessment of the case
   - Balanced view of both sides
   - Likely outcome considerations
   - Key factors that will determine the case

{case_context}Case Text:
{case_text[:4000]}

Format your response as:
PRO-PLAINTIFF ARGUMENTS:
[detailed analysis]

PRO-DEFENDANT ARGUMENTS:
[detailed analysis]

NEUTRAL ANALYSIS:
[balanced assessment]"""

        summary_text = await self._generate_ai_summary(prompt, max_tokens=2000)
        
        # Parse the response
        contrastive = self._parse_contrastive_summary(summary_text)
        
        return {
            "pro_plaintiff": {
                "arguments": contrastive.get("pro_plaintiff", ""),
                "key_facts": contrastive.get("plaintiff_facts", []),
                "legal_principles": contrastive.get("plaintiff_principles", [])
            },
            "pro_defendant": {
                "arguments": contrastive.get("pro_defendant", ""),
                "key_facts": contrastive.get("defendant_facts", []),
                "legal_principles": contrastive.get("defendant_principles", [])
            },
            "neutral_analysis": contrastive.get("neutral", ""),
            "raw_response": summary_text
        }
    
    def _parse_contrastive_summary(self, text: str) -> Dict[str, Any]:
        """Parse contrastive summary from AI response"""
        result = {
            "pro_plaintiff": "",
            "pro_defendant": "",
            "neutral": "",
            "plaintiff_facts": [],
            "defendant_facts": [],
            "plaintiff_principles": [],
            "defendant_principles": []
        }
        
        current_section = None
        current_text = []
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                if current_section and current_text:
                    if current_section in result:
                        result[current_section] = ' '.join(current_text)
                    current_text = []
                continue
            
            if 'PRO-PLAINTIFF' in line.upper() or 'PRO PLAINTIFF' in line.upper():
                if current_section and current_text:
                    if current_section in result:
                        result[current_section] = ' '.join(current_text)
                current_section = 'pro_plaintiff'
                current_text = [line.split(':', 1)[1].strip()] if ':' in line else []
            elif 'PRO-DEFENDANT' in line.upper() or 'PRO DEFENDANT' in line.upper():
                if current_section and current_text:
                    if current_section in result:
                        result[current_section] = ' '.join(current_text)
                current_section = 'pro_defendant'
                current_text = [line.split(':', 1)[1].strip()] if ':' in line else []
            elif 'NEUTRAL' in line.upper():
                if current_section and current_text:
                    if current_section in result:
                        result[current_section] = ' '.join(current_text)
                current_section = 'neutral'
                current_text = [line.split(':', 1)[1].strip()] if ':' in line else []
            elif current_section:
                current_text.append(line)
        
        # Save last section
        if current_section and current_text:
            if current_section in result:
                result[current_section] = ' '.join(current_text)
        
        # Fallbacks
        if not result["pro_plaintiff"]:
            result["pro_plaintiff"] = "Unable to extract pro-plaintiff arguments"
        if not result["pro_defendant"]:
            result["pro_defendant"] = "Unable to extract pro-defendant arguments"
        if not result["neutral"]:
            result["neutral"] = "Unable to extract neutral analysis"
        
        return result

