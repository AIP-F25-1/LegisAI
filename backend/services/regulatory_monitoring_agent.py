"""
Regulatory Monitoring Agent Service
Periodically crawls open regulation datasets and flags new legal requirements
"""

import logging
import asyncio
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

@dataclass
class RegulatoryUpdate:
    """New regulatory requirement detected"""
    regulation_id: str
    title: str
    description: str
    jurisdiction: str
    effective_date: str
    source: str
    impact_level: str  # "low", "medium", "high", "critical"
    affected_clauses: List[str]
    suggested_updates: List[str]
    url: Optional[str] = None

@dataclass
class ClauseUpdateSuggestion:
    """Suggestion for updating a clause based on new regulations"""
    clause_type: str
    current_clause: str
    suggested_update: str
    reason: str
    regulation_reference: str
    priority: str  # "low", "medium", "high", "critical"

class RegulatoryMonitoringAgent:
    """Monitors regulatory changes and suggests clause updates"""
    
    def __init__(self, ollama_client=None, ollama_model: str = "llama3.1:8b", vector_store=None):
        """
        Initialize regulatory monitoring agent
        
        Args:
            ollama_client: Ollama client for AI analysis
            ollama_model: Model name to use
            vector_store: VectorStore for searching regulations
        """
        self.ollama_client = ollama_client
        self.ollama_model = ollama_model
        self.vector_store = vector_store
        
        # Track last check time
        self.last_check_time = {}
        
        # Regulation sources (can be extended with actual API integrations)
        self.regulation_sources = {
            "US": [
                "Federal Register",
                "CFR (Code of Federal Regulations)",
                "State regulations"
            ],
            "EU": [
                "EUR-Lex",
                "EU Official Journal",
                "Member State regulations"
            ],
            "UK": [
                "UK Legislation",
                "Statutory Instruments",
                "Regulatory updates"
            ]
        }
    
    async def crawl_regulation_datasets(
        self,
        jurisdiction: str = "US",
        max_results: int = 20,
        days_back: int = 30
    ) -> List[RegulatoryUpdate]:
        """
        Periodically crawl open regulation datasets
        
        Args:
            jurisdiction: Jurisdiction to monitor (US, EU, UK)
            max_results: Maximum number of updates to return
            days_back: Number of days to look back
            
        Returns:
            List of regulatory updates
        """
        logger.info(f"📡 Crawling regulation datasets for {jurisdiction}...")
        
        # In a real implementation, this would:
        # 1. Connect to regulation APIs (Federal Register, EUR-Lex, etc.)
        # 2. Parse RSS feeds or API responses
        # 3. Extract new regulations
        # For now, we'll simulate with sample data and use AI to generate realistic updates
        
        updates = []
        
        # Simulate finding regulations (in production, this would be real API calls)
        sample_updates = await self._simulate_regulation_crawl(jurisdiction, days_back)
        
        # Use AI to analyze and enhance if available
        if self.ollama_client:
            for sample in sample_updates[:max_results]:
                enhanced = await self._enhance_regulation_with_ai(sample, jurisdiction)
                if enhanced:
                    updates.append(enhanced)
                else:
                    updates.append(sample)
        else:
            updates = sample_updates[:max_results]
        
        # Store last check time
        self.last_check_time[jurisdiction] = datetime.now()
        
        logger.info(f"✅ Found {len(updates)} regulatory updates for {jurisdiction}")
        return updates
    
    async def _simulate_regulation_crawl(self, jurisdiction: str, days_back: int) -> List[RegulatoryUpdate]:
        """Simulate regulation crawl (replace with real API calls in production)"""
        updates = []
        
        # Sample regulations based on jurisdiction
        if jurisdiction == "US":
            updates = [
                RegulatoryUpdate(
                    regulation_id="US_REG_2024_001",
                    title="Updated Data Privacy Requirements",
                    description="New requirements for data breach notification and consumer data protection",
                    jurisdiction="US",
                    effective_date=(datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
                    source="Federal Register",
                    impact_level="high",
                    affected_clauses=["data_privacy", "confidentiality", "data_protection"],
                    suggested_updates=["Add data breach notification requirements", "Update privacy policy language"],
                    url="https://federalregister.gov/example"
                ),
                RegulatoryUpdate(
                    regulation_id="US_REG_2024_002",
                    title="Enhanced Consumer Protection Standards",
                    description="Stricter requirements for consumer contracts and unfair terms",
                    jurisdiction="US",
                    effective_date=(datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"),
                    source="CFR",
                    impact_level="medium",
                    affected_clauses=["consumer_protection", "terms_and_conditions"],
                    suggested_updates=["Review unfair terms clauses", "Add consumer rights language"],
                    url="https://ecfr.gov/example"
                )
            ]
        elif jurisdiction == "EU":
            updates = [
                RegulatoryUpdate(
                    regulation_id="EU_REG_2024_001",
                    title="GDPR Enforcement Updates",
                    description="New guidance on GDPR compliance and data subject rights",
                    jurisdiction="EU",
                    effective_date=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                    source="EUR-Lex",
                    impact_level="high",
                    affected_clauses=["data_protection", "gdpr_compliance", "privacy"],
                    suggested_updates=["Update GDPR compliance language", "Add data subject rights section"],
                    url="https://eur-lex.europa.eu/example"
                )
            ]
        elif jurisdiction == "UK":
            updates = [
                RegulatoryUpdate(
                    regulation_id="UK_REG_2024_001",
                    title="Post-Brexit Regulatory Changes",
                    description="Updated requirements following UK regulatory framework changes",
                    jurisdiction="UK",
                    effective_date=(datetime.now() - timedelta(days=12)).strftime("%Y-%m-%d"),
                    source="UK Legislation",
                    impact_level="medium",
                    affected_clauses=["governing_law", "jurisdiction", "compliance"],
                    suggested_updates=["Update governing law clauses", "Review jurisdiction provisions"],
                    url="https://legislation.gov.uk/example"
                )
            ]
        
        return updates
    
    async def _enhance_regulation_with_ai(self, regulation: RegulatoryUpdate, jurisdiction: str) -> Optional[RegulatoryUpdate]:
        """Enhance regulation details using AI"""
        try:
            prompt = f"""Analyze this regulatory update and provide detailed impact assessment:

REGULATION: {regulation.title}
DESCRIPTION: {regulation.description}
JURISDICTION: {jurisdiction}
EFFECTIVE DATE: {regulation.effective_date}

Provide:
1. IMPACT LEVEL: Assess impact (low/medium/high/critical)
2. AFFECTED CLAUSES: List specific clause types affected
3. SUGGESTED UPDATES: Provide actionable update suggestions
4. PRIORITY: How urgent is this update?

Format:
IMPACT LEVEL: [level]
AFFECTED CLAUSES:
- [clause 1]
- [clause 2]
SUGGESTED UPDATES:
- [update 1]
- [update 2]"""
            
            if hasattr(self.ollama_client, 'generate') and asyncio.iscoroutinefunction(self.ollama_client.generate):
                response = await self.ollama_client.generate(
                    model=self.ollama_model,
                    prompt=prompt,
                    options={'temperature': 0.3, 'top_p': 0.9, 'num_predict': 600}
                )
                analysis = response.response if hasattr(response, 'response') else str(response)
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
                            options={'temperature': 0.3, 'top_p': 0.9, 'num_predict': 600}
                        )
                    )
                    response = await asyncio.wait_for(future, timeout=60.0)
                    analysis = response.response if hasattr(response, 'response') else str(response)
            
            # Parse AI response and update regulation
            parsed = self._parse_regulation_analysis(analysis)
            if parsed:
                regulation.impact_level = parsed.get('impact_level', regulation.impact_level)
                regulation.affected_clauses = parsed.get('affected_clauses', regulation.affected_clauses)
                regulation.suggested_updates = parsed.get('suggested_updates', regulation.suggested_updates)
            
            return regulation
        except Exception as e:
            logger.warning(f"AI enhancement failed: {e}")
            return regulation
    
    def _parse_regulation_analysis(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse AI analysis of regulation"""
        result = {
            'impact_level': 'medium',
            'affected_clauses': [],
            'suggested_updates': []
        }
        
        current_section = None
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if 'IMPACT LEVEL' in line.upper():
                if 'critical' in line.lower():
                    result['impact_level'] = 'critical'
                elif 'high' in line.lower():
                    result['impact_level'] = 'high'
                elif 'low' in line.lower():
                    result['impact_level'] = 'low'
            elif 'AFFECTED CLAUSES' in line.upper():
                current_section = 'clauses'
            elif 'SUGGESTED UPDATES' in line.upper():
                current_section = 'updates'
            elif line.startswith('-') or line.startswith('•'):
                content = line[1:].strip()
                if current_section == 'clauses':
                    result['affected_clauses'].append(content)
                elif current_section == 'updates':
                    result['suggested_updates'].append(content)
        
        return result
    
    async def flag_new_requirements(
        self,
        contract_text: str,
        jurisdiction: str = "US",
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Flag new legal requirements and suggest clause updates
        
        Args:
            contract_text: Contract text to analyze
            jurisdiction: Jurisdiction to check
            days_back: Number of days to look back for new regulations
            
        Returns:
            Dictionary with flagged requirements and suggested updates
        """
        logger.info(f"🚩 Flagging new legal requirements for contract...")
        
        # Get recent regulatory updates
        updates = await self.crawl_regulation_datasets(jurisdiction, max_results=20, days_back=days_back)
        
        # Analyze contract against new regulations
        flagged_requirements = []
        clause_updates = []
        
        for update in updates:
            # Check if contract is affected by this regulation
            is_affected = self._check_contract_affected(contract_text, update)
            
            if is_affected:
                flagged_requirements.append(update)
                
                # Generate clause update suggestions
                suggestions = await self._generate_clause_updates(contract_text, update)
                clause_updates.extend(suggestions)
        
        return {
            "jurisdiction": jurisdiction,
            "check_date": datetime.now().strftime("%Y-%m-%d"),
            "days_back": days_back,
            "total_regulations_found": len(updates),
            "flagged_requirements": [self._regulation_to_dict(r) for r in flagged_requirements],
            "clause_update_suggestions": [self._clause_update_to_dict(c) for c in clause_updates],
            "summary": {
                "critical_updates": len([r for r in flagged_requirements if r.impact_level == "critical"]),
                "high_updates": len([r for r in flagged_requirements if r.impact_level == "high"]),
                "medium_updates": len([r for r in flagged_requirements if r.impact_level == "medium"]),
                "total_suggestions": len(clause_updates)
            }
        }
    
    def _check_contract_affected(self, contract_text: str, regulation: RegulatoryUpdate) -> bool:
        """Check if contract is affected by a regulation"""
        contract_lower = contract_text.lower()
        
        # Check if contract mentions affected clause types
        for clause_type in regulation.affected_clauses:
            clause_keywords = {
                "data_privacy": ["data", "privacy", "personal information", "pii"],
                "confidentiality": ["confidential", "non-disclosure", "nda"],
                "data_protection": ["data protection", "gdpr", "data security"],
                "consumer_protection": ["consumer", "customer", "user"],
                "terms_and_conditions": ["terms", "conditions", "agreement"],
                "governing_law": ["governing law", "jurisdiction", "applicable law"],
                "compliance": ["compliance", "regulatory", "legal requirement"]
            }
            
            keywords = clause_keywords.get(clause_type, [clause_type])
            if any(keyword in contract_lower for keyword in keywords):
                return True
        
        return False
    
    async def _generate_clause_updates(
        self,
        contract_text: str,
        regulation: RegulatoryUpdate
    ) -> List[ClauseUpdateSuggestion]:
        """Generate specific clause update suggestions"""
        suggestions = []
        
        # Use AI to generate specific suggestions if available
        if self.ollama_client:
            for clause_type in regulation.affected_clauses:
                prompt = f"""Based on this new regulation, suggest a specific clause update:

REGULATION: {regulation.title}
DESCRIPTION: {regulation.description}
AFFECTED CLAUSE TYPE: {clause_type}
CURRENT CONTRACT CONTEXT: {contract_text[:1000]}

Provide:
1. CURRENT CLAUSE: Identify the relevant clause in the contract
2. SUGGESTED UPDATE: Provide updated clause text
3. REASON: Explain why this update is needed
4. PRIORITY: Rate priority (low/medium/high/critical)

Format:
CURRENT CLAUSE: [clause text]
SUGGESTED UPDATE: [updated clause]
REASON: [explanation]
PRIORITY: [level]"""
                
                try:
                    if hasattr(self.ollama_client, 'generate') and asyncio.iscoroutinefunction(self.ollama_client.generate):
                        response = await self.ollama_client.generate(
                            model=self.ollama_model,
                            prompt=prompt,
                            options={'temperature': 0.4, 'top_p': 0.9, 'num_predict': 800}
                        )
                        analysis = response.response if hasattr(response, 'response') else str(response)
                    else:
                        loop = asyncio.get_event_loop()
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = loop.run_in_executor(
                                executor,
                                lambda: self.ollama_client.generate(
                                    model=self.ollama_model,
                                    prompt=prompt,
                                    options={'temperature': 0.4, 'top_p': 0.9, 'num_predict': 800}
                                )
                            )
                            response = await asyncio.wait_for(future, timeout=60.0)
                            analysis = response.response if hasattr(response, 'response') else str(response)
                    
                    parsed = self._parse_clause_update(analysis, clause_type, regulation.regulation_id)
                    if parsed:
                        suggestions.append(parsed)
                except Exception as e:
                    logger.warning(f"Error generating clause update: {e}")
        
        # Fallback: Use regulation's suggested updates
        if not suggestions:
            for update_text in regulation.suggested_updates:
                suggestions.append(ClauseUpdateSuggestion(
                    clause_type=regulation.affected_clauses[0] if regulation.affected_clauses else "general",
                    current_clause="[To be identified]",
                    suggested_update=update_text,
                    reason=f"Required by {regulation.title}",
                    regulation_reference=regulation.regulation_id,
                    priority=regulation.impact_level
                ))
        
        return suggestions
    
    def _parse_clause_update(self, text: str, clause_type: str, regulation_id: str) -> Optional[ClauseUpdateSuggestion]:
        """Parse clause update suggestion from AI response"""
        current_clause = ""
        suggested_update = ""
        reason = ""
        priority = "medium"
        
        current_section = None
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if 'CURRENT CLAUSE' in line.upper():
                current_section = 'current'
                if ':' in line:
                    current_clause = line.split(':', 1)[1].strip()
            elif 'SUGGESTED UPDATE' in line.upper():
                current_section = 'suggested'
                if ':' in line:
                    suggested_update = line.split(':', 1)[1].strip()
            elif 'REASON' in line.upper():
                current_section = 'reason'
                if ':' in line:
                    reason = line.split(':', 1)[1].strip()
            elif 'PRIORITY' in line.upper():
                if 'critical' in line.lower():
                    priority = 'critical'
                elif 'high' in line.lower():
                    priority = 'high'
                elif 'low' in line.lower():
                    priority = 'low'
            elif current_section == 'current':
                current_clause += " " + line
            elif current_section == 'suggested':
                suggested_update += " " + line
            elif current_section == 'reason':
                reason += " " + line
        
        if suggested_update:
            return ClauseUpdateSuggestion(
                clause_type=clause_type,
                current_clause=current_clause[:500] if current_clause else "[To be identified]",
                suggested_update=suggested_update[:1000],
                reason=reason[:500] if reason else f"Required by regulation {regulation_id}",
                regulation_reference=regulation_id,
                priority=priority
            )
        return None
    
    def _regulation_to_dict(self, regulation: RegulatoryUpdate) -> Dict[str, Any]:
        """Convert RegulatoryUpdate to dictionary"""
        return {
            "regulation_id": regulation.regulation_id,
            "title": regulation.title,
            "description": regulation.description,
            "jurisdiction": regulation.jurisdiction,
            "effective_date": regulation.effective_date,
            "source": regulation.source,
            "impact_level": regulation.impact_level,
            "affected_clauses": regulation.affected_clauses,
            "suggested_updates": regulation.suggested_updates,
            "url": regulation.url
        }
    
    def _clause_update_to_dict(self, suggestion: ClauseUpdateSuggestion) -> Dict[str, Any]:
        """Convert ClauseUpdateSuggestion to dictionary"""
        return {
            "clause_type": suggestion.clause_type,
            "current_clause": suggestion.current_clause,
            "suggested_update": suggestion.suggested_update,
            "reason": suggestion.reason,
            "regulation_reference": suggestion.regulation_reference,
            "priority": suggestion.priority
        }
    
    def get_last_check_time(self, jurisdiction: str) -> Optional[str]:
        """Get last check time for a jurisdiction"""
        if jurisdiction in self.last_check_time:
            return self.last_check_time[jurisdiction].strftime("%Y-%m-%d %H:%M:%S")
        return None

