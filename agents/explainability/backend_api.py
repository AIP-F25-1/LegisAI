from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from .cross_consistency import cross_consistency_check

app = FastAPI(title="LegisAI Backend", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

class CheckReq(BaseModel):
    clause: str

@app.post("/api/check-consistency")
def check(req: CheckReq):
    """Run all 5 dummy agents + consistency auditor."""
    return cross_consistency_check(req.clause)

@app.get("/health")
def health():
    return {"ok": True}

# Run:  uvicorn agents.backend_api:app --reload
