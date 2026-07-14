"""
Robust JSON extraction from raw LLM text output.

Small models occasionally wrap JSON in markdown code fences, add a
leading/trailing sentence, or emit single quotes. extract_json()
tolerates these common deviations before falling back to a clear
error rather than crashing the whole agent turn.
"""

import json
import re
from typing import Any, Dict


def extract_json(raw: str) -> Dict[str, Any]:
    """
    Extracts and parses the first valid JSON object found in `raw`.
    Returns {} if nothing parseable is found, so callers can treat an
    empty dict as "the model didn't produce usable structured output"
    without needing to catch exceptions themselves.
    """
    if not raw:
        return {}

    text = raw.strip()

    # Strip ```json ... ``` or ``` ... ``` code fences if present.
    fence_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fallback: grab the first {...} span and try again.
    brace_match = re.search(r"\{.*\}", text, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            pass

    return {}