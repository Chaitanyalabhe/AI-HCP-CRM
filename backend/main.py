from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agent import run_agent
import tools
from database import SessionLocal, Interaction
from langchain_core.messages import HumanMessage, AIMessage
from models import ChatRequest, ChatResponse, SaveInteractionRequest, SaveInteractionResponse, InteractionResponse
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conversation_history = []


@app.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    global conversation_history
    result_messages = run_agent(payload.message, conversation_history)

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