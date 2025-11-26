from fastapi import FastAPI
from pydantic import BaseModel
from cross_consistency import run_cross_consistency

app = FastAPI(title="LegisAI Explainability Backend")

class ClauseRequest(BaseModel):
    clause: str

@app.get("/")
def root():
    return {"message": "LegisAI Explainability Backend Running"}

@app.post("/cross_consistency")
def cross_consistency_api(req: ClauseRequest):
    try:
        result = run_cross_consistency(req.clause)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}
