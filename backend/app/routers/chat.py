"""
Chat router.

Implements POST /chat — the conversational Log Interaction path.

Responsibilities of this router (deliberately kept separate from the
agent itself):
1. Resolve or create a ChatSession for the rep.
2. Persist the incoming user message.
3. Invoke the LangGraph agent (app.agent.graph.run_agent), which
   owns intent routing and tool execution.
4. Persist the agent's reply (and a tool-invocation message, if a
   tool ran).
5. Return a ChatResponse matching the frontend's chatSlice contract.

The agent itself (app/agent/graph.py) is intentionally DB-session-aware
via dependency injection rather than opening its own session, so
everything in a single chat turn happens within one transaction.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.chat import ChatMessage, ChatSession
from app.models.rep import Rep
from app.schemas.chat import ChatRequest, ChatResponse
from app.agent.graph import run_agent

router = APIRouter(prefix="/chat", tags=["Chat"])


def _get_or_create_session(db: Session, rep_id: int, session_id: int | None) -> ChatSession:
    if session_id:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if session:
            return session

    rep = db.query(Rep).filter(Rep.id == rep_id).first()
    if not rep:
        raise HTTPException(status_code=404, detail=f"Rep {rep_id} not found")

    session = ChatSession(rep_id=rep_id)
    db.add(session)
    db.flush()
    return session


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    session = _get_or_create_session(db, payload.rep_id, payload.session_id)

    # Persist the user's message first so the agent's history-loading
    # (inside run_agent) sees the full conversation including this turn.
    user_message = ChatMessage(session_id=session.id, role="user", content=payload.message)
    db.add(user_message)
    db.commit()

    result = run_agent(db=db, session_id=session.id, rep_id=payload.rep_id, message=payload.message)

    if result.get("tool_name"):
        db.add(
            ChatMessage(
                session_id=session.id,
                role="tool",
                tool_name=result["tool_name"],
                content=result.get("tool_summary", ""),
            )
        )

    db.add(ChatMessage(session_id=session.id, role="assistant", content=result["reply"]))
    db.commit()

    return ChatResponse(
        session_id=session.id,
        reply=result["reply"],
        tool_name=result.get("tool_name"),
        tool_summary=result.get("tool_summary"),
        tool_result=result.get("tool_result"),
    )