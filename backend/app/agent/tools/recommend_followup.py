"""
Recommend Follow-up tool.

Looks at the rep's most relevant recent interaction (by mentioned
doctor, or their latest logged interaction) and asks the LLM for one
concrete next-best-action.
"""

from typing import Any, Dict

from app.agent.prompts import search_parse_prompt, recommendation_prompt
from app.agent.llm_client import generate, generate_json
from app.agent.state import AgentState
from app.schemas.interaction import InteractionOut
from app.services import interaction_service


def run(state: AgentState) -> Dict[str, Any]:
    db = state["db"]
    message = state["message"]
    rep_id = state["rep_id"]

    parsed = generate_json(search_parse_prompt(message))
    hcp_name = parsed.get("hcp_name")

    matches = interaction_service.list_interactions(db, rep_id=rep_id, hcp_name=hcp_name or None, limit=1)
    if not matches:
        return {
            "tool_name": "recommend_followup",
            "tool_result": {"error": "No interaction found to base a recommendation on."},
            "tool_summary": "I don't have a logged interaction to base a recommendation on yet.",
        }

    latest = matches[0]
    context = InteractionOut.model_validate(latest).model_dump(mode="json")
    recommendation = generate(recommendation_prompt(context))

    return {
        "tool_name": "recommend_followup",
        "tool_result": {"doctor_name": latest.doctor_name, "recommendation": recommendation},
        "tool_summary": recommendation,
    }