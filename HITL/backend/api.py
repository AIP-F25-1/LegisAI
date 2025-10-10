# HITL/backend/api.py
from fastapi import FastAPI
from .feedback_handler import save_feedback

app = FastAPI()  # 👈 THIS must exist at the top level!

@app.get("/")
def read_root():
    return {"message": "HITL backend running successfully!"}

@app.post("/submit_feedback/")
def submit_feedback(feedback: dict):
    save_feedback(feedback)
    return {"status": "success", "data": feedback}
