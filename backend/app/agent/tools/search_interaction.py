"""
Search Interaction tool.

Parses a natural-language query into structured filters via the LLM
and delegates to interaction_service.list_interactions — the same
search logic backing GET /interaction for the dashboard.
"""

from typing import Any, Dict

from app.agent.prompts import search_parse_prompt
from app.agent.llm_client import generate_json
from app.agent.state import AgentState
from app.schemas.interaction import InteractionOut
from app.services import interaction_service


def run(state: AgentState) -> Dict[str, Any]:
    db = state["db"]
    message = state["message"]
    rep_id = state["rep_id"]

    filters = generate_json(search_parse_prompt(message))

    matches = interaction_service.list_interactions(
        db,
        q=filters.get("q") or None,
        hcp_name=filters.get("hcp_name") or None,
        hospital=filters.get("hospital") or None,
        product=filters.get("product") or None,
        date_from=filters.get("date_from") or None,
        date_to=filters.get("date_to") or None,
        rep_id=rep_id,
        limit=20,
    )

    results = [InteractionOut.model_validate(m).model_dump(mode="json") for m in matches]

    summary = f"Found {len(results)} matching interaction(s)."

    return {
        "tool_name": "search_interaction",
        "tool_result": {"count": len(results), "interactions": results},
        "tool_summary": summary,
    }