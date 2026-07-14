"""
Summarize Previous Interactions tool.

Identifies which doctor the rep is asking about, pulls their past
interaction summaries, and asks the LLM to roll them up into a short
pre-meeting briefing.
"""

from typing import Any, Dict

from app.agent.prompts import search_parse_prompt, rollup_summary_prompt
from app.agent.llm_client import generate, generate_json
from app.agent.state import AgentState
from app.services import interaction_service


def run(state: AgentState) -> Dict[str, Any]:
    db = state["db"]
    message = state["message"]
    rep_id = state["rep_id"]

    parsed = generate_json(search_parse_prompt(message))
    doctor_name = parsed.get("hcp_name")

    if not doctor_name:
        return {
            "tool_name": "summarize_previous",
            "tool_result": {"error": "No doctor name recognized in the message."},
            "tool_summary": "I couldn't tell which doctor you're asking about.",
        }

    history = interaction_service.get_interactions_for_hcp(db, doctor_name=doctor_name, limit=20)
    history = [h for h in history if h.rep_id == rep_id] or history

    if not history:
        return {
            "tool_name": "summarize_previous",
            "tool_result": {"doctor_name": doctor_name, "briefing": "No prior interactions found."},
            "tool_summary": f"No prior interactions found with {doctor_name}.",
        }

    past_summaries = [h.summary for h in history if h.summary]
    briefing = generate(rollup_summary_prompt(doctor_name, past_summaries))

    return {
        "tool_name": "summarize_previous",
        "tool_result": {
            "doctor_name": doctor_name,
            "interaction_count": len(history),
            "briefing": briefing,
        },
        "tool_summary": briefing,
    }