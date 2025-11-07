"""
backend_api.py
-------------------------------------------------------
FastAPI backend for LegisAI — Explainability & Cross-Consistency Layer.
This API routes requests from the frontend to the agent orchestration engine.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
import traceback

# ✅ Ensure the 'agents' folder is discoverable
sys.path.append(os.path.abspath("."))

# ✅ Import your cross-consistency logic
from agents.explainability.cross_consistency import run_cross_consistency


# ------------------------------------------------------
# ⚙️ FastAPI App Setup
# ------------------------------------------------------
app = FastAPI(
    title="LegisAI Backend API",
    description="Backend API for Explainability & Multi-Agent Consistency Layer",
    version="1.0.0"
)

# Allow all CORS (for testing; later restrict for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------
# 🧠 Request Schema
# ------------------------------------------------------
class ClauseRequest(BaseModel):
    clause: str


# ------------------------------------------------------
# ✅ Routes
# ------------------------------------------------------

@app.get("/")
def root():
    return {"message": "LegisAI backend is running successfully 🚀"}


@app.post("/cross_consistency")
async def cross_consistency_endpoint(req: ClauseRequest):
    """
    Accepts a clause and runs the multi-agent consistency check.
    """
    try:
        clause_text = req.clause
        print(f"🔹 Received clause: {clause_text}")

        # Run the consistency layer
        result = run_cross_consistency(clause_text)

        return {"status": "ok", "result": result}

    except Exception as e:
        print("❌ Error during cross-consistency run:")
        traceback.print_exc()
        return {"status": "error", "error": str(e)}


# ------------------------------------------------------
# 🧪 Run directly (for debugging)
# ------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend_api:app", host="127.0.0.1", port=8000, reload=True)
