from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agent import run_agent
import tools
from database import SessionLocal, Interaction
from langchain_core.messages import HumanMessage, AIMessage
from models import ChatRequest, ChatResponse, SaveInteractionRequest, SaveInteractionResponse, InteractionResponse
from typing import List
import os

app = FastAPI()

_cors_origins_env = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)
_cors_origins = [o.strip() for o in _cors_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conversation_history = []

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    global conversation_history
    try:
        result_messages = run_agent(payload.message, conversation_history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    new_msgs = [m for m in result_messages if isinstance(m, (HumanMessage, AIMessage))]
    conversation_history = new_msgs[-20:]

    ai_response = ""
    for msg in reversed(result_messages):
        if isinstance(msg, AIMessage) and msg.content:
            ai_response = msg.content
            break

    return ChatResponse(
        response=ai_response or "Form updated successfully!",
        form_data=tools.interaction_state
    )


@app.post("/save", response_model=SaveInteractionResponse)
async def save_interaction(payload: SaveInteractionRequest):
    db = SessionLocal()
    try:
        interaction = Interaction(**payload.model_dump())
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        return SaveInteractionResponse(success=True, id=interaction.id)
    finally:
        db.close()


@app.get("/interactions", response_model=List[InteractionResponse])
async def get_interactions():
    db = SessionLocal()
    try:
        return db.query(Interaction).order_by(Interaction.created_at.desc()).all()
    finally:
        db.close()


@app.get("/health")
async def health():
    return {"status": "ok"}