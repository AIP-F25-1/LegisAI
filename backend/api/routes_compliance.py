from fastapi import APIRouter, UploadFile, File, HTTPException
from agents.crew import run_compliance
import io, pdfplumber

router = APIRouter(prefix="/api/compliance", tags=["compliance"])

@router.post("/check")
async def check_contract(file: UploadFile = File(...)):
    try:
        data = await file.read()
        text = ""
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for p in pdf.pages:
                text += p.extract_text() or ""
        report = run_compliance(text)
        return {"report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
