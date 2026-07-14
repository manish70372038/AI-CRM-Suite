"""
Groq LLM client wrapper.

Centralizes all LLM calls so every tool and prompt in the agent goes
through one place — makes it trivial to swap models, add retries, or
adjust temperature policy without touching individual tools.

Two entrypoints:
- generate(): plain text completion (used for summaries, chat replies)
- generate_json(): completion where the model is instructed to return
  only JSON, which is then parsed via app.utils.json_parser
"""

from functools import lru_cache
from typing import Any, Dict, List, Optional

from groq import Groq

from app.config import settings
from app.utils.json_parser import extract_json


@lru_cache
def get_client() -> Groq:
    """Returns a cached Groq client instance for the process lifetime."""
    return Groq(api_key=settings.GROQ_API_KEY)


def generate(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: float = 0.3,
    max_tokens: int = 1024,
) -> str:
    """
    Plain text completion. `messages` follows the standard
    [{"role": "system"|"user"|"assistant", "content": "..."}] shape.
    """
    client = get_client()
    
    
    active_model = model or "llama-3.3-70b-versatile"
    
    response = client.chat.completions.create(
        model=active_model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()


def generate_json(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: float = 0.1,
    max_tokens: int = 1024,
) -> Dict[str, Any]:
    """
    Completion where the model is expected to return strictly JSON.
    Appends a reinforcing instruction to the last message and parses
    the result via extract_json, which tolerates minor formatting
    issues (e.g. accidental markdown code fences) that small models
    sometimes produce.
    """
    reinforced_messages = messages + [
        {
            "role": "system",
            "content": "Respond with ONLY valid JSON. No explanations, no markdown, no code fences.",
        }
    ]
    
    active_model = model or "llama-3.3-70b-versatile"
    
    raw = generate(
        reinforced_messages, 
        model=active_model, 
        temperature=temperature, 
        max_tokens=max_tokens
    )
    return extract_json(raw)