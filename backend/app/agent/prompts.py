"""
Prompt templates for the LangGraph agent.

Every function here returns a `messages` list ready to pass to
app.agent.llm_client.generate() / generate_json(). Keeping all prompt
text in one module makes it easy to iterate on wording/schema without
hunting through tool implementation files.
"""

from datetime import date
from typing import List, Dict, Optional


VALID_INTENTS = [
    "log_interaction",
    "edit_interaction",
    "search_interaction",
    "summarize_previous",
    "recommend_followup",
    "clarify",
]


def intent_router_prompt(message: str, history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Classifies a user message into one of the 5 tool intents (or
    'clarify' if genuinely ambiguous). Few-shot examples anchor the
    small model to consistent categorical output.
    """
    history_text = "\n".join(f"{h['role']}: {h['content']}" for h in history[-6:]) or "(no prior messages)"

    system = f"""You are an intent classifier for a pharmaceutical sales CRM assistant.
Classify the user's latest message into EXACTLY ONE of these intents:

- log_interaction: user is describing a new meeting/call/email with a doctor to be recorded
- edit_interaction: user wants to change/update/correct a previously logged interaction
- search_interaction: user wants to find/look up/retrieve past interaction(s)
- summarize_previous: user wants a rollup/summary of past visits with a doctor
- recommend_followup: user wants a suggestion for what to do next

If the message is a greeting, unrelated, or too vague to classify, use "clarify".

Examples:
"Met Dr. Sharma at Apollo, discussed Cardivex, follow up in 2 weeks" -> log_interaction
"Change the follow-up date on my last visit to next Friday" -> edit_interaction
"Show me my meetings with Dr. Sharma last month" -> search_interaction
"What's the history with Dr. Patel?" -> summarize_previous
"What should I do next with Dr. Sharma?" -> recommend_followup
"Hi there" -> clarify

Conversation so far:
{history_text}

Respond with ONLY a JSON object: {{"intent": "<one of the intents above>"}}"""

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": message},
    ]


def log_interaction_extraction_prompt(raw_text: str) -> List[Dict[str, str]]:
    """
    Extracts structured entities from free-text describing an HCP
    interaction. Grounded with today's date so relative follow-up
    expressions ("in 2 weeks", "next Friday") resolve to real dates.
    """
    today = date.today().isoformat()

    system = f"""You are a life-sciences CRM assistant extracting structured data from a
pharmaceutical sales rep's description of a doctor interaction.

Today's date is {today}. Use it to resolve relative dates like "in 2 weeks" or "next Friday"
into an absolute date in YYYY-MM-DD format.

Extract and return ONLY this JSON structure:
{{
  "doctor_name": "<full name, e.g. 'Dr. Ayesha Sharma', or empty string if not mentioned>",
  "hospital": "<hospital/clinic name, or empty string if not mentioned>",
  "interaction_type": "<one of: visit, call, email, virtual — infer from context, default 'visit'>",
  "products_discussed": ["<product 1>", "<product 2>"],
  "follow_up_date": "<YYYY-MM-DD, or empty string if no follow-up mentioned>",
  "sentiment": "<one of: positive, neutral, negative — infer doctor's receptiveness>",
  "summary": "<a concise 2-3 sentence professional summary of the interaction>"
}}"""

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": raw_text},
    ]


def edit_extraction_prompt(instruction: str, current_record: Dict) -> List[Dict[str, str]]:
    """
    Parses a natural-language edit instruction into a diff constrained
    to allowed, editable fields on an existing interaction record.
    """
    today = date.today().isoformat()

    system = f"""You are parsing an edit instruction for an existing CRM interaction record.
Today's date is {today}.

Current record:
{current_record}

The user will describe a change in natural language. Return ONLY a JSON object containing
JUST the fields that should change, using this schema (omit fields that aren't changing):
{{
  "doctor_name": "<string>",
  "hospital": "<string>",
  "interaction_type": "<visit|call|email|virtual>",
  "products_discussed": ["<string>", ...],
  "summary": "<string>",
  "follow_up_date": "<YYYY-MM-DD>",
  "follow_up_action": "<string>",
  "sentiment": "<positive|neutral|negative>"
}}

If the instruction doesn't map to any allowed field, return an empty JSON object {{}}."""

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": instruction},
    ]


def search_parse_prompt(query: str) -> List[Dict[str, str]]:
    """
    Parses a natural-language search query into structured filter
    parameters matching interaction_service.list_interactions()'s
    accepted arguments.
    """
    today = date.today().isoformat()

    system = f"""You are parsing a search query for a CRM interaction search.
Today's date is {today}.

Return ONLY a JSON object with any of these optional fields (omit ones not mentioned):
{{
  "hcp_name": "<doctor name mentioned, if any>",
  "hospital": "<hospital mentioned, if any>",
  "product": "<product mentioned, if any>",
  "date_from": "<YYYY-MM-DD, if a time range start is implied>",
  "date_to": "<YYYY-MM-DD, if a time range end is implied>",
  "q": "<a general free-text fallback term if nothing more specific applies>"
}}"""

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": query},
    ]


def rollup_summary_prompt(doctor_name: str, past_summaries: List[str]) -> List[Dict[str, str]]:
    """Rolls up multiple past interaction summaries into a trend overview."""
    joined = "\n".join(f"- {s}" for s in past_summaries) if past_summaries else "(no prior notes)"

    system = f"""You are a life-sciences CRM assistant. Summarize the interaction history with
{doctor_name} into a concise, useful briefing (3-5 sentences) a sales rep can read right before
their next meeting. Highlight trends, product interest, objections, and overall sentiment
trajectory. Respond in plain text, not JSON."""

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Past interaction summaries:\n{joined}"},
    ]


def recommendation_prompt(interaction_context: Dict) -> List[Dict[str, str]]:
    """
    Suggests a next-best-action based on a single interaction's
    summary, sentiment, and products discussed.
    """
    system = """You are a life-sciences sales strategy assistant. Based on the interaction
details provided, suggest ONE concise, specific, actionable next step for the sales rep
to take with this doctor (e.g. sending specific materials, scheduling a demo, addressing
an objection). Respond in 1-2 sentences of plain text, not JSON."""

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": str(interaction_context)},
    ]


def chat_reply_prompt(tool_name: Optional[str], tool_result: Optional[Dict], user_message: str) -> List[Dict[str, str]]:
    """
    Generates the final conversational reply shown to the rep after a
    tool has run (or after a 'clarify' intent, where no tool runs).
    """
    if tool_name:
        context = f"A '{tool_name}' action was just completed with this result: {tool_result}"
    else:
        context = "No specific CRM action was identified from the message."

    system = f"""You are a friendly, professional CRM assistant for pharmaceutical sales reps.
{context}

Write a brief, natural conversational reply (1-3 sentences) confirming what happened or
guiding the rep on what to say next. Do not use JSON. Be concise and professional."""

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_message},
    ]