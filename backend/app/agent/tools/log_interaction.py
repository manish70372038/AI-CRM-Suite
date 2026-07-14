"""
Log Interaction tool.

Takes the rep's free-text description of a doctor meeting/call/email,
extracts structured entities via the LLM (doctor name, hospital,
products, follow-up date, sentiment, summary), resolves/creates the
matching HCP record, and persists a new Interaction row — the same
row shape the Form Mode POST /interaction endpoint produces.
"""

from typing import Any, Dict

from app.agent.prompts import log_interaction_extraction_prompt
from app.agent.llm_client import generate_json
from app.agent.state import AgentState
from app.models.interaction import SourceType
from app.schemas.interaction import InteractionCreate, InteractionOut
from app.services import interaction_service


def run(state: AgentState) -> Dict[str, Any]:
    db = state["db"]
    message = state["message"]
    rep_id = state["rep_id"]

    extracted = generate_json(log_interaction_extraction_prompt(message))

    payload = InteractionCreate(
        rep_id=rep_id,
        doctor_name=extracted.get("doctor_name") or "Unknown",
        hospital=extracted.get("hospital") or None,
        interaction_type=extracted.get("interaction_type") or "visit",
        products_discussed=extracted.get("products_discussed") or [],
        summary=extracted.get("summary") or None,
        raw_notes=message,
        follow_up_date=extracted.get("follow_up_date") or None,
        sentiment=extracted.get("sentiment") or None,
        source=SourceType.chat,
    )

    interaction = interaction_service.create_interaction(db, payload)
    result = InteractionOut.model_validate(interaction).model_dump(mode="json")

    summary = f"Logged a {interaction.interaction_type.value} with {interaction.doctor_name}"
    if interaction.hospital:
        summary += f" at {interaction.hospital}"
    summary += "."

    return {
        "tool_name": "log_interaction",
        "tool_result": result,
        "tool_summary": summary,
    }