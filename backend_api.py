from fastapi import FastAPI
from pydantic import BaseModel
from cross_consistency import run_cross_consistency

app = FastAPI()

class ClauseInput(BaseModel):
    text: str

@app.post("/analyze")
def analyze_clause(data: ClauseInput):
    return run_cross_consistency(data.text)

@app.get("/")
def root():
    return {"message": "LegisAI Explainability API is running."}
