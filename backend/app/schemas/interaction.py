"""
Pydantic schemas for Interaction records.

These schemas are the single contract shared between:
- FastAPI routers (request validation / response serialization)
- The LangGraph tools (log_interaction, edit_interaction, etc.), which
  build/return data conforming to these same shapes so the API and the
  AI agent never disagree on what a valid interaction looks like.
"""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.interaction import InteractionType, SentimentType, SourceType


class InteractionBase(BaseModel):
    doctor_name: str = Field(..., min_length=1, max_length=150)
    hospital: Optional[str] = Field(default=None, max_length=200)
    interaction_type: InteractionType = InteractionType.visit
    products_discussed: List[str] = Field(default_factory=list)
    summary: Optional[str] = None
    raw_notes: Optional[str] = None
    follow_up_date: Optional[date] = None
    follow_up_action: Optional[str] = None
    sentiment: Optional[SentimentType] = None


class InteractionCreate(InteractionBase):
    rep_id: int
    hcp_id: Optional[int] = None
    source: SourceType = SourceType.form

    @field_validator("products_discussed", mode="before")
    @classmethod
    def coerce_products(cls, value):
        """Allow a comma-separated string as a convenience for callers
        that haven't split it into a list yet (e.g. raw LLM output)."""
        if isinstance(value, str):
            return [p.strip() for p in value.split(",") if p.strip()]
        return value or []


class InteractionUpdate(BaseModel):
    """All fields optional — supports partial updates via PUT."""

    doctor_name: Optional[str] = None
    hospital: Optional[str] = None
    interaction_type: Optional[InteractionType] = None
    products_discussed: Optional[List[str]] = None
    summary: Optional[str] = None
    raw_notes: Optional[str] = None
    follow_up_date: Optional[date] = None
    follow_up_action: Optional[str] = None
    sentiment: Optional[SentimentType] = None
    hcp_id: Optional[int] = None


class InteractionOut(InteractionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rep_id: int
    hcp_id: Optional[int] = None
    source: SourceType
    created_at: datetime
    updated_at: datetime