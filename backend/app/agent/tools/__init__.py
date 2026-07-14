"""
Aggregates the 5 LangGraph tool entrypoints so graph.py can dispatch
on intent via one import: `from app.agent.tools import TOOL_MAP`.

Each tool module exposes a single `run(state) -> dict` function that
returns a partial AgentState update (tool_name, tool_result,
tool_summary).
"""

from app.agent.tools import (
    log_interaction,
    edit_interaction,
    search_interaction,
    summarize_previous,
    recommend_followup,
)

TOOL_MAP = {
    "log_interaction": log_interaction.run,
    "edit_interaction": edit_interaction.run,
    "search_interaction": search_interaction.run,
    "summarize_previous": summarize_previous.run,
    "recommend_followup": recommend_followup.run,
}

__all__ = ["TOOL_MAP"]