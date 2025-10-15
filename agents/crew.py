from crewai import Crew, Process
from agents.compliance.agent import ComplianceAgent
from agents.monitoring.agent import MonitoringAgent
from agents.risk.agent import RiskAgent
from agents.compliance.tasks import compliance_task
from agents.monitoring.tasks import monitoring_task
from agents.risk.tasks import risk_task

def run_compliance(contract_text: str):
    t = compliance_task(contract_text); t.agent = ComplianceAgent
    return Crew(agents=[ComplianceAgent], tasks=[t], process=Process.sequential).kickoff()

def run_monitoring():
    t = monitoring_task(); t.agent = MonitoringAgent
    return Crew(agents=[MonitoringAgent], tasks=[t], process=Process.sequential).kickoff()

def run_risk(contract_text: str, p_def: float, lgd: float):
    t = risk_task(contract_text, p_def, lgd); t.agent = RiskAgent
    return Crew(agents=[RiskAgent], tasks=[t], process=Process.sequential).kickoff()
