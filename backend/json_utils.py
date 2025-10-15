import json
from pydantic import BaseModel, ValidationError
from typing import List, Any

class ClauseItem(BaseModel):
    clause_id: int
    text: str
    status: str
    rationale: str
    citations: List[str] = []

def extract_json(raw: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{"); end = raw.rfind("}")
        if start >= 0 and end > start:
            return json.loads(raw[start:end+1])
        start = raw.find("["); end = raw.rfind("]")
        if start >= 0 and end > start:
            return json.loads(raw[start:end+1])
        raise
