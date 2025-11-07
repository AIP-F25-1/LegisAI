from fastapi import FastAPI
from agents.explainability.cross_consistency import run_cross_consistency

app = FastAPI(title="LegisAI Backend API")

@app.get("/")
def root():
    return {"message": "LegisAI Backend Running"}

@app.post("/cross_consistency")
def check_clause(data: dict):
    clause = data.get("clause", "")
    if not clause:
        return {"error": "No clause provided"}
    result = run_cross_consistency(clause)
    return result
