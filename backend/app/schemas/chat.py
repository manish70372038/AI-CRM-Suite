"""
Pydantic schemas for the conversational chat endpoint.

ChatResponse's `tool_result` is intentionally typed as a loose dict
because different tools return different shapes (e.g. log_interaction
returns an InteractionOut-like dict, search_interaction returns a
list wrapped in a dict, recommend_followup returns a suggestion
string). Routers/tools are still responsible for keeping these
shapes internally consistent per tool_name.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    rep_id: int
    session_id: Optional[int] = None


class ChatResponse(BaseModel):
    session_id: int
    reply: str
    tool_name: Optional[str] = None
    tool_summary: Optional[str] = None
    tool_result: Optional[Dict[str, Any]] = None