"""
LangGraph agent definition.

Graph shape:

    route_intent --(conditional)--> one of the 5 tool nodes --> respond --> END
                  --(conditional)--> clarify -------------------> respond --> END

`run_agent()` is the single public entrypoint called by
routers/chat.py. It builds the initial AgentState (loading recent
chat history for context), invokes the compiled graph, and returns
the fields the router needs (reply, tool_name, tool_summary,
tool_result).
"""

from typing import Any, Dict, List

from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session

from app.agent.state import AgentState
from app.agent.prompts import intent_router_prompt, chat_reply_prompt, VALID_INTENTS
from app.agent.llm_client import generate, generate_json
from app.agent.tools import TOOL_MAP
from app.models.chat import ChatMessage


def _load_history(db: Session, session_id: int, limit: int = 12) -> List[Dict[str, str]]:
    """Loads recent user/assistant turns (tool messages excluded) for prompt context."""
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id, ChatMessage.role.in_(["user", "assistant"]))
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .all()
    )
    messages.reverse()
    return [{"role": m.role, "content": m.content} for m in messages]


def _route_intent(state: AgentState) -> Dict[str, Any]:
    result = generate_json(intent_router_prompt(state["message"], state.get("history", [])))
    intent = result.get("intent")
    if intent not in VALID_INTENTS:
        intent = "clarify"
    return {"intent": intent}


def _clarify(state: AgentState) -> Dict[str, Any]:
    return {"tool_name": None, "tool_result": None, "tool_summary": None}


def _respond(state: AgentState) -> Dict[str, Any]:
    reply = generate(chat_reply_prompt(state.get("tool_name"), state.get("tool_result"), state["message"]))
    return {"reply": reply}


def _select_branch(state: AgentState) -> str:
    return state["intent"] if state["intent"] in TOOL_MAP else "clarify"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("route_intent", _route_intent)
    graph.add_node("clarify", _clarify)
    graph.add_node("respond", _respond)

    for name, tool_fn in TOOL_MAP.items():
        graph.add_node(name, tool_fn)
        graph.add_edge(name, "respond")

    graph.set_entry_point("route_intent")
    graph.add_conditional_edges(
        "route_intent",
        _select_branch,
        {**{name: name for name in TOOL_MAP}, "clarify": "clarify"},
    )
    graph.add_edge("clarify", "respond")
    graph.add_edge("respond", END)

    return graph.compile()


_compiled_graph = None


def _get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph


def run_agent(db: Session, session_id: int, rep_id: int, message: str) -> Dict[str, Any]:
    """
    Single entrypoint used by routers/chat.py. Builds initial state,
    invokes the compiled LangGraph, and returns the fields the router
    needs to persist and respond with.
    """
    history = _load_history(db, session_id)

    initial_state: AgentState = {
        "message": message,
        "rep_id": rep_id,
        "session_id": session_id,
        "db": db,
        "history": history,
    }

    final_state = _get_graph().invoke(initial_state)

    return {
        "reply": final_state.get("reply", ""),
        "tool_name": final_state.get("tool_name"),
        "tool_summary": final_state.get("tool_summary"),
        "tool_result": final_state.get("tool_result"),
    }