from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from agents.crew import run_risk
import io, pdfplumber, json
from backend.schemas import RiskRequest

router = APIRouter(prefix="/api/risk", tags=["risk"])

@router.post("/score")
async def risk_score(
    file: UploadFile = File(...),
    payload: str = Form('{"p_default":0.05,"lgd":0.6}')
):
    """Send multipart: file + payload (JSON string)."""
    try:
        req = RiskRequest(**json.loads(payload))
        data = await file.read()
        text = ""
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for p in pdf.pages:
                text += p.extract_text() or ""
        result = run_risk(text, req.p_default, req.lgd)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
