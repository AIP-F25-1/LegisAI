from fastapi import APIRouter, HTTPException
from agents.crew import run_monitoring

router = APIRouter(prefix="/api/monitor", tags=["monitoring"])

@router.post("/run")
async def run_monitor():
    try:
        res = run_monitoring()
        return {"changes": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
