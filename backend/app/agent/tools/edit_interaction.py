"""
Edit Interaction tool.

Resolves which interaction record a natural-language edit instruction
refers to (by mentioned doctor name, falling back to the rep's most
recent interaction), asks the LLM to turn the instruction into a
field-level diff, and applies it via interaction_service.update_interaction
— the same path used by the PUT /interaction/{id} endpoint.
"""

from typing import Any, Dict, Optional

from app.agent.prompts import edit_extraction_prompt, search_parse_prompt
from app.agent.llm_client import generate_json
from app.agent.state import AgentState
from app.schemas.interaction import InteractionOut, InteractionUpdate
from app.services import interaction_service


def _find_target_interaction(db, rep_id: int, message: str):
    parsed = generate_json(search_parse_prompt(message))
    hcp_name = parsed.get("hcp_name")

    matches = interaction_service.list_interactions(db, rep_id=rep_id, hcp_name=hcp_name or None, limit=1)
    if matches:
        return matches[0]

    # Fallback: most recent interaction for this rep, regardless of doctor.
    fallback = interaction_service.list_interactions(db, rep_id=rep_id, limit=1)
    return fallback[0] if fallback else None


def run(state: AgentState) -> Dict[str, Any]:
    db = state["db"]
    message = state["message"]
    rep_id = state["rep_id"]

    target = _find_target_interaction(db, rep_id, message)
    if not target:
        return {
            "tool_name": "edit_interaction",
            "tool_result": {"error": "No existing interaction found to edit."},
            "tool_summary": "I couldn't find an existing interaction to edit.",
        }

    current_record = InteractionOut.model_validate(target).model_dump(mode="json")
    diff = generate_json(edit_extraction_prompt(message, current_record))

    if not diff:
        return {
            "tool_name": "edit_interaction",
            "tool_result": {"error": "No recognizable change in instruction.", "interaction": current_record},
            "tool_summary": "I couldn't tell what to change on that interaction.",
        }

    update_payload = InteractionUpdate(**diff)
    updated = interaction_service.update_interaction(db, target.id, update_payload)
    result = InteractionOut.model_validate(updated).model_dump(mode="json")

    changed_fields = ", ".join(diff.keys())
    summary = f"Updated {updated.doctor_name}'s interaction ({changed_fields})."

    return {
        "tool_name": "edit_interaction",
        "tool_result": result,
        "tool_summary": summary,
    }