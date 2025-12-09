"""
Domain Compliance Packs
Specialized compliance rules for different domains: finance, healthcare, labor, GDPR/CCPA
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ComplianceRule:
    """Single compliance rule"""
    rule_id: str
    domain: str
    jurisdiction: str
    rule_text: str
    severity: str  # "critical", "high", "medium", "low"
    keywords: List[str]
    description: str

class DomainCompliancePacks:
    """Domain-specific compliance rule packs"""
    
    def __init__(self):
        """Initialize domain compliance packs"""
        self.packs = {
            "finance": self._get_finance_rules(),
            "healthcare": self._get_healthcare_rules(),
            "labor": self._get_labor_rules(),
            "gdpr": self._get_gdpr_rules(),
            "ccpa": self._get_ccpa_rules(),
            "general": self._get_general_rules()
        }
    
    def _get_finance_rules(self) -> List[ComplianceRule]:
        """Finance domain compliance rules"""
        return [
            ComplianceRule(
                rule_id="FIN-001",
                domain="finance",
                jurisdiction="US",
                rule_text="Financial contracts must include clear interest rate disclosure",
                severity="critical",
                keywords=["interest rate", "APR", "annual percentage rate", "finance charge"],
                description="Required by Truth in Lending Act (TILA)"
            ),
            ComplianceRule(
                rule_id="FIN-002",
                domain="finance",
                jurisdiction="US",
                rule_text="Loan agreements must include right of rescission disclosure",
                severity="high",
                keywords=["right of rescission", "three-day", "cooling-off period"],
                description="Required for certain consumer credit transactions"
            ),
            ComplianceRule(
                rule_id="FIN-003",
                domain="finance",
                jurisdiction="US",
                rule_text="Securities contracts must comply with SEC regulations",
                severity="critical",
                keywords=["securities", "SEC", "investment", "offering"],
                description="Securities Act of 1933 and Securities Exchange Act of 1934"
            ),
            ComplianceRule(
                rule_id="FIN-004",
                domain="finance",
                jurisdiction="US",
                rule_text="Banking contracts must comply with FDIC regulations",
                severity="critical",
                keywords=["bank", "deposit", "FDIC", "insured"],
                description="Federal Deposit Insurance Act"
            )
        ]
    
    def _get_healthcare_rules(self) -> List[ComplianceRule]:
        """Healthcare domain compliance rules"""
        return [
            ComplianceRule(
                rule_id="HC-001",
                domain="healthcare",
                jurisdiction="US",
                rule_text="Healthcare contracts must include HIPAA compliance clauses",
                severity="critical",
                keywords=["HIPAA", "PHI", "protected health information", "health data"],
                description="Health Insurance Portability and Accountability Act"
            ),
            ComplianceRule(
                rule_id="HC-002",
                domain="healthcare",
                jurisdiction="US",
                rule_text="Medical service agreements must include patient privacy notice",
                severity="high",
                keywords=["patient privacy", "medical records", "confidentiality"],
                description="HIPAA Privacy Rule requirement"
            ),
            ComplianceRule(
                rule_id="HC-003",
                domain="healthcare",
                jurisdiction="US",
                rule_text="Healthcare provider contracts must comply with Stark Law",
                severity="critical",
                keywords=["physician", "referral", "Stark Law", "self-referral"],
                description="Physician Self-Referral Law (Stark Law)"
            ),
            ComplianceRule(
                rule_id="HC-004",
                domain="healthcare",
                jurisdiction="US",
                rule_text="Pharmaceutical contracts must comply with FDA regulations",
                severity="critical",
                keywords=["pharmaceutical", "drug", "FDA", "prescription"],
                description="Food, Drug, and Cosmetic Act"
            )
        ]
    
    def _get_labor_rules(self) -> List[ComplianceRule]:
        """Labor domain compliance rules"""
        return [
            ComplianceRule(
                rule_id="LAB-001",
                domain="labor",
                jurisdiction="US",
                rule_text="Employment contracts must comply with FLSA minimum wage requirements",
                severity="critical",
                keywords=["minimum wage", "FLSA", "Fair Labor Standards", "hourly rate"],
                description="Fair Labor Standards Act"
            ),
            ComplianceRule(
                rule_id="LAB-002",
                domain="labor",
                jurisdiction="US",
                rule_text="Employment agreements must include at-will employment disclaimer if applicable",
                severity="high",
                keywords=["at-will", "employment", "termination", "dismissal"],
                description="State-specific employment law"
            ),
            ComplianceRule(
                rule_id="LAB-003",
                domain="labor",
                jurisdiction="US",
                rule_text="Non-compete clauses must be reasonable in scope and duration",
                severity="high",
                keywords=["non-compete", "non-competition", "restrictive covenant"],
                description="State-specific enforceability requirements"
            ),
            ComplianceRule(
                rule_id="LAB-004",
                domain="labor",
                jurisdiction="US",
                rule_text="Employment contracts must comply with ADA accommodation requirements",
                severity="critical",
                keywords=["disability", "ADA", "accommodation", "reasonable accommodation"],
                description="Americans with Disabilities Act"
            ),
            ComplianceRule(
                rule_id="LAB-005",
                domain="labor",
                jurisdiction="US",
                rule_text="Employment agreements must include FMLA leave rights if applicable",
                severity="high",
                keywords=["FMLA", "family leave", "medical leave", "leave of absence"],
                description="Family and Medical Leave Act"
            )
        ]
    
    def _get_gdpr_rules(self) -> List[ComplianceRule]:
        """GDPR compliance rules"""
        return [
            ComplianceRule(
                rule_id="GDPR-001",
                domain="gdpr",
                jurisdiction="EU",
                rule_text="Data processing agreements must include lawful basis for processing",
                severity="critical",
                keywords=["lawful basis", "consent", "legitimate interest", "data processing"],
                description="GDPR Article 6"
            ),
            ComplianceRule(
                rule_id="GDPR-002",
                domain="gdpr",
                jurisdiction="EU",
                rule_text="Contracts must include data subject rights notification",
                severity="critical",
                keywords=["data subject rights", "access", "erasure", "portability"],
                description="GDPR Articles 15-22"
            ),
            ComplianceRule(
                rule_id="GDPR-003",
                domain="gdpr",
                jurisdiction="EU",
                rule_text="Data breach notification clauses must comply with 72-hour requirement",
                severity="critical",
                keywords=["data breach", "notification", "72 hours", "personal data breach"],
                description="GDPR Article 33"
            ),
            ComplianceRule(
                rule_id="GDPR-004",
                domain="gdpr",
                jurisdiction="EU",
                rule_text="Data processing agreements must include Data Protection Impact Assessment (DPIA) if required",
                severity="high",
                keywords=["DPIA", "impact assessment", "high risk processing"],
                description="GDPR Article 35"
            )
        ]
    
    def _get_ccpa_rules(self) -> List[ComplianceRule]:
        """CCPA compliance rules"""
        return [
            ComplianceRule(
                rule_id="CCPA-001",
                domain="ccpa",
                jurisdiction="US-CA",
                rule_text="Privacy policies must include CCPA consumer rights disclosure",
                severity="critical",
                keywords=["CCPA", "California Consumer Privacy", "consumer rights", "opt-out"],
                description="California Consumer Privacy Act"
            ),
            ComplianceRule(
                rule_id="CCPA-002",
                domain="ccpa",
                jurisdiction="US-CA",
                rule_text='Data collection agreements must include "Do Not Sell My Personal Information" option',
                severity="critical",
                keywords=["do not sell", "personal information", "sale of data"],
                description="CCPA Section 1798.135"
            ),
            ComplianceRule(
                rule_id="CCPA-003",
                domain="ccpa",
                jurisdiction="US-CA",
                rule_text="Contracts must include disclosure of categories of personal information collected",
                severity="high",
                keywords=["categories", "personal information", "data collection"],
                description="CCPA Section 1798.100"
            )
        ]
    
    def _get_general_rules(self) -> List[ComplianceRule]:
        """General compliance rules"""
        return [
            ComplianceRule(
                rule_id="GEN-001",
                domain="general",
                jurisdiction="US",
                rule_text="Contracts must include dispute resolution clause",
                severity="medium",
                keywords=["dispute", "arbitration", "mediation", "litigation"],
                description="General contract best practice"
            ),
            ComplianceRule(
                rule_id="GEN-002",
                domain="general",
                jurisdiction="US",
                rule_text="Contracts must include governing law clause",
                severity="medium",
                keywords=["governing law", "jurisdiction", "choice of law"],
                description="General contract best practice"
            )
        ]
    
    def get_rules_for_domains(
        self,
        domains: List[str],
        jurisdiction: Optional[str] = None
    ) -> List[ComplianceRule]:
        """
        Get compliance rules for specified domains
        
        Args:
            domains: List of domain names (finance, healthcare, labor, gdpr, ccpa, general)
            jurisdiction: Optional jurisdiction filter
            
        Returns:
            List of compliance rules
        """
        all_rules = []
        
        for domain in domains:
            if domain.lower() in self.packs:
                rules = self.packs[domain.lower()]
                if jurisdiction:
                    rules = [r for r in rules if r.jurisdiction == jurisdiction]
                all_rules.extend(rules)
        
        return all_rules
    
    def check_compliance(
        self,
        contract_text: str,
        domains: List[str],
        jurisdiction: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check contract against domain-specific compliance rules
        
        Args:
            contract_text: Contract text to check
            domains: List of domains to check
            jurisdiction: Optional jurisdiction filter
            
        Returns:
            Compliance check results
        """
        rules = self.get_rules_for_domains(domains, jurisdiction)
        contract_lower = contract_text.lower()
        
        violations = []
        warnings = []
        passed = []
        
        for rule in rules:
            # Check if any keywords are present
            keyword_found = any(
                keyword.lower() in contract_lower
                for keyword in rule.keywords
            )
            
            if keyword_found:
                # Check if rule text is satisfied
                rule_satisfied = rule.rule_text.lower() in contract_lower or any(
                    keyword.lower() in contract_lower
                    for keyword in rule.keywords
                )
                
                if not rule_satisfied:
                    if rule.severity in ["critical", "high"]:
                        violations.append({
                            "rule_id": rule.rule_id,
                            "domain": rule.domain,
                            "severity": rule.severity,
                            "rule_text": rule.rule_text,
                            "description": rule.description,
                            "keywords_found": [
                                kw for kw in rule.keywords
                                if kw.lower() in contract_lower
                            ]
                        })
                    else:
                        warnings.append({
                            "rule_id": rule.rule_id,
                            "domain": rule.domain,
                            "severity": rule.severity,
                            "rule_text": rule.rule_text,
                            "description": rule.description
                        })
                else:
                    passed.append({
                        "rule_id": rule.rule_id,
                        "domain": rule.domain,
                        "rule_text": rule.rule_text
                    })
        
        return {
            "domains_checked": domains,
            "jurisdiction": jurisdiction,
            "total_rules": len(rules),
            "violations": violations,
            "warnings": warnings,
            "passed": passed,
            "compliance_score": (
                len(passed) / len(rules) if rules else 1.0
            ),
            "critical_violations": len([v for v in violations if v["severity"] == "critical"]),
            "high_violations": len([v for v in violations if v["severity"] == "high"])
        }
    
    def get_available_domains(self) -> List[str]:
        """Get list of available domain packs"""
        return list(self.packs.keys())
    
    def get_domain_info(self, domain: str) -> Dict[str, Any]:
        """Get information about a domain pack"""
        if domain.lower() not in self.packs:
            return {"error": f"Domain '{domain}' not found"}
        
        rules = self.packs[domain.lower()]
        return {
            "domain": domain.lower(),
            "rule_count": len(rules),
            "jurisdictions": list(set(r.jurisdiction for r in rules)),
            "severity_breakdown": {
                "critical": len([r for r in rules if r.severity == "critical"]),
                "high": len([r for r in rules if r.severity == "high"]),
                "medium": len([r for r in rules if r.severity == "medium"]),
                "low": len([r for r in rules if r.severity == "low"])
            },
            "rules": [
                {
                    "rule_id": r.rule_id,
                    "severity": r.severity,
                    "rule_text": r.rule_text,
                    "description": r.description
                }
                for r in rules
            ]
        }

