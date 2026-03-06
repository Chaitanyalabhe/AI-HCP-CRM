from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import TypedDict, Annotated, Sequence
import operator
import os
from dotenv import load_dotenv
from tools import log_interaction, edit_interaction, summarize_interaction, suggest_follow_up, save_interaction_to_db

load_dotenv()

SYSTEM_PROMPT = """You are an AI assistant for a pharmaceutical CRM system helping field representatives log their HCP (Healthcare Professional) interactions.

You have access to these tools:
1. log_interaction - Extract details from natural language and populate the form
2. edit_interaction - Update specific fields when user corrects information
3. summarize_interaction - Clean up messy notes into structured format
4. suggest_follow_up - Recommend next steps based on interaction context
5. save_interaction_to_db - Save the interaction when user confirms

IMPORTANT RULES:
- Always use tools to respond — never just describe what you would do
- For new interactions, use log_interaction
- For corrections (words like "sorry", "actually", "change", "update"), use edit_interaction
- Today's date format: YYYY-MM-DD
- Extract sentiment from context: positive words → Positive, negative → Negative, neutral → Neutral
- If user says "today", use today's actual date
- Always confirm what fields were filled after using a tool
"""

tools = [log_interaction, edit_interaction, summarize_interaction, suggest_follow_up, save_interaction_to_db]

_groq_api_key = os.getenv("GROQ_API_KEY")
if not _groq_api_key:
    raise RuntimeError(
        "Missing GROQ_API_KEY. Set it in the environment (e.g., Render service env vars)."
    )

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=_groq_api_key,
    temperature=0,
).bind_tools(tools)


class AgentState(TypedDict):
    messages: Annotated[Sequence, operator.add]


def agent_node(state: AgentState):
    messages = state["messages"]
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
    response = llm.invoke(messages)
    return {"messages": [response]}


def should_continue(state: AgentState):
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END


tool_node = ToolNode(tools)

graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
graph.add_edge("tools", "agent")

app = graph.compile()


def run_agent(user_message: str, history: list = []):
    messages = history + [HumanMessage(content=user_message)]
    result = app.invoke({"messages": messages})
    return result["messages"]