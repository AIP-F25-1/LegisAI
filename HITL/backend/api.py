from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.runnables import RunnableConfig
from langgraph_setup import graph, State

app = FastAPI()

# ✅ Allow requests from your frontend (React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173"] if using Vite
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "HITL backend is running!"}

@app.post("/api/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("prompt")
    input_state = State(messages=[("user", user_message)])

    config = RunnableConfig(configurable={"thread_id": "1"}, recursion_limit=10)
    events = graph.stream(
        input=input_state,
        config=config,
        stream_mode="values",
        interrupt_before=["tools"]
    )

    last_event = None
    for event in events:
        last_event = event

    checkpoint_id = config.checkpoint_id
    return {
        "message": last_event["messages"][-1].content,
        "checkpoint_id": checkpoint_id
    }

@app.post("/api/resume")
async def resume(request: Request):
    data = await request.json()
    checkpoint_id = data.get("checkpoint_id")

    config = RunnableConfig(configurable={"thread_id": "1", "checkpoint_id": checkpoint_id}, recursion_limit=10)
    events = graph.stream(input=None, config=config, stream_mode="values")

    last_event = None
    for event in events:
        last_event = event

    return {"message": last_event["messages"][-1].content}
