# dummy_backend.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# --- Initialize FastAPI ---
app = FastAPI(title="Dummy LegisAI Backend")  # <-- Make sure this line exists and is not indented

# --- Enable CORS (so Streamlit can talk to it) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request Schema ---
class ChatRequest(BaseModel):
    message: str

# --- Dummy Chat Route ---
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    user_msg = request.message
    reply = f"🤖 [Dummy Backend Reply] You asked: '{user_msg}'"
    return {"reply": reply}

# --- Health Check ---
@app.get("/")
async def root():
    return {"message": "Dummy backend is running!"}
