"""
Agent state definition.

LangGraph passes this dict through every node in the graph (intent
router -> tool node -> response formatter). Each node reads what it
needs and returns a partial update that LangGraph merges in.

`db` and `rep_id`/`session_id` are included directly in state (rather
than threaded through as separate function args) because LangGraph
node functions only receive `state` — this is the standard pattern
for giving tool nodes access to request-scoped resources.
"""

from typing import Any, Dict, List, Optional, TypedDict


class AgentState(TypedDict, total=False):
    # --- Input ---
    message: str
    rep_id: int
    session_id: int
    db: Any  # SQLAlchemy Session, injected per-request by run_agent()
    history: List[Dict[str, str]]  # prior {role, content} turns for context

    # --- Routing ---
    intent: Optional[str]  # one of: log_interaction, edit_interaction,
    # search_interaction, summarize_previous, recommend_followup, clarify

    # --- Tool execution ---
    tool_name: Optional[str]
    tool_result: Optional[Dict[str, Any]]
    tool_summary: Optional[str]

    # --- Output ---
    reply: Optional[str]