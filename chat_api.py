from fastapi import FastAPI
from pydantic import BaseModel
from chatbot.router import process_user_message
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    text: str

@app.post("/chat")
async def chat_endpoint(message: Message):
    response = process_user_message(message.text)
    return {"reply": response}

@app.get("/")
def root():
    return {"msg": "Chatbot backend is running"}
