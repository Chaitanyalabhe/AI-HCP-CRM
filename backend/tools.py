from langchain_core.tools import tool
from datetime import date, datetime
from typing import Optional
import json

# In-memory state (shared with agent)
interaction_state = {}

@tool
def log_interaction(
    hcp_name: str,
    interaction_type: str = "Meeting",
    date: str = None,
    time: str = None,
    attendees: str = "",
    topics_discussed: str = "",
    sentiment: str = "Neutral",
    materials_shared: str = "",
    samples_distributed: str = "",
    follow_up_required: bool = False,
    next_steps: str = ""
) -> dict:
    """
    Log a new HCP interaction by extracting details from natural language.
    Use this when user describes a new meeting or interaction with an HCP.
    """
    global interaction_state
    today = date.today().strftime("%Y-%m-%d") if not date else date
    now = datetime.now().strftime("%I:%M %p") if not time else time

    interaction_state = {
        "hcp_name": hcp_name,
        "interaction_type": interaction_type,
        "date": today,
        "time": now,
        "attendees": attendees,
        "topics_discussed": topics_discussed,
        "sentiment": sentiment,
        "materials_shared": materials_shared,
        "samples_distributed": samples_distributed,
        "follow_up_required": follow_up_required,
        "next_steps": next_steps
    }
    return {"success": True, "action": "log", "data": interaction_state}


@tool
def edit_interaction(
    hcp_name: Optional[str] = None,
    interaction_type: Optional[str] = None,
    date: Optional[str] = None,
    time: Optional[str] = None,
    attendees: Optional[str] = None,
    topics_discussed: Optional[str] = None,
    sentiment: Optional[str] = None,
    materials_shared: Optional[str] = None,
    samples_distributed: Optional[str] = None,
    follow_up_required: Optional[bool] = None,
    next_steps: Optional[str] = None
) -> dict:
    """
    Edit specific fields of the current interaction without changing others.
    Use this when user wants to correct or update specific details.
    Only update fields that are explicitly mentioned by the user.
    """
    global interaction_state
    updates = {k: v for k, v in {
        "hcp_name": hcp_name,
        "interaction_type": interaction_type,
        "date": date,
        "time": time,
        "attendees": attendees,
        "topics_discussed": topics_discussed,
        "sentiment": sentiment,
        "materials_shared": materials_shared,
        "samples_distributed": samples_distributed,
        "follow_up_required": follow_up_required,
        "next_steps": next_steps
    }.items() if v is not None}

    interaction_state.update(updates)
    return {"success": True, "action": "edit", "data": interaction_state, "updated_fields": list(updates.keys())}


@tool
def summarize_interaction(raw_notes: str) -> dict:
    """
    Summarize long or messy interaction notes into clean, structured topics discussed.
    Use this when user provides lengthy or unstructured notes that need cleaning up.
    """
    # The LLM will handle summarization via the agent; this tool signals the action
    return {
        "success": True,
        "action": "summarize",
        "raw_notes": raw_notes,
        "instruction": "Summarize these notes into key bullet points for the topics_discussed field"
    }


@tool
def suggest_follow_up(topics_discussed: str, sentiment: str, hcp_name: str) -> dict:
    """
    Analyze the interaction and suggest next steps or follow-up actions for the field rep.
    Use this when user asks for recommendations or next steps after an interaction.
    """
    return {
        "success": True,
        "action": "suggest_follow_up",
        "context": {
            "hcp_name": hcp_name,
            "topics": topics_discussed,
            "sentiment": sentiment
        },
        "instruction": "Based on this interaction context, suggest specific follow-up actions"
    }


@tool
def save_interaction_to_db(interaction_data: str) -> dict:
    """
    Save the current interaction data to the database permanently.
    Use this when user says 'save', 'submit', 'confirm' or 'store this interaction'.
    The interaction_data should be a JSON string of the current form state.
    """
    return {
        "success": True,
        "action": "save_to_db",
        "data": interaction_data,
        "message": "Interaction saved to database successfully"
    }