import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes_compliance import router as compliance_router
from backend.api.routes_risk import router as risk_router
from backend.api.routes_monitoring import router as monitor_router
from backend.api.routes_stream import router as stream_router
from backend import deps

app = FastAPI(title="LegisAI Backend")

origins = os.getenv("CORS_ORIGINS","*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(compliance_router)
app.include_router(risk_router)
app.include_router(monitor_router)
app.include_router(stream_router)

# start scheduler
deps.start_jobs()

@app.get("/api/health")
def health():
    return {"ok": True}
