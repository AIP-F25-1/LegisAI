from pydantic import BaseModel
from typing import Any

class RiskRequest(BaseModel):
    p_default: float = 0.05
    lgd: float = 0.6

class ComplianceResponse(BaseModel):
    report: Any

class MonitorResponse(BaseModel):
    changes: Any

class RiskResponse(BaseModel):
    result: Any
