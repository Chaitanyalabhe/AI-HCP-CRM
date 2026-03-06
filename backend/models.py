from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ── Request Models (what frontend sends) ──────────────────────────

class ChatRequest(BaseModel):
    message: str

class SaveInteractionRequest(BaseModel):
    hcp_name: Optional[str] = ""
    interaction_type: Optional[str] = "Meeting"
    date: Optional[str] = ""
    time: Optional[str] = ""
    attendees: Optional[str] = ""
    topics_discussed: Optional[str] = ""
    sentiment: Optional[str] = "Neutral"
    materials_shared: Optional[str] = ""
    samples_distributed: Optional[str] = ""
    follow_up_required: Optional[bool] = False
    next_steps: Optional[str] = ""

# ── Response Models (what backend returns) ────────────────────────

class ChatResponse(BaseModel):
    response: str
    form_data: dict

class SaveInteractionResponse(BaseModel):
    success: bool
    id: int
    message: str = "Interaction saved successfully"

class InteractionResponse(BaseModel):
    id: int
    hcp_name: Optional[str]
    interaction_type: Optional[str]
    date: Optional[str]
    time: Optional[str]
    attendees: Optional[str]
    topics_discussed: Optional[str]
    sentiment: Optional[str]
    materials_shared: Optional[str]
    samples_distributed: Optional[str]
    follow_up_required: Optional[bool]
    next_steps: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True  # allows SQLAlchemy model → Pydantic conversion