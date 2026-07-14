"""
Interaction model — the core CRM record.

Field names/enums here are the ground truth that
app.schemas.interaction and app.services.interaction_service both
build on top of.
"""

import enum

from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, Enum as SAEnum, JSON, func
from sqlalchemy.orm import relationship

from app.database import Base


class InteractionType(str, enum.Enum):
    visit = "visit"
    call = "call"
    email = "email"
    virtual = "virtual"


class SentimentType(str, enum.Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"


class SourceType(str, enum.Enum):
    form = "form"
    chat = "chat"


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    rep_id = Column(Integer, ForeignKey("reps.id"), nullable=False, index=True)
    hcp_id = Column(Integer, ForeignKey("hcps.id"), nullable=True, index=True)

    doctor_name = Column(String(150), nullable=False)
    hospital = Column(String(200), nullable=True)
    interaction_type = Column(SAEnum(InteractionType), nullable=False, default=InteractionType.visit)
    products_discussed = Column(JSON, nullable=False, default=list)

    summary = Column(Text, nullable=True)
    raw_notes = Column(Text, nullable=True)

    follow_up_date = Column(Date, nullable=True)
    follow_up_action = Column(Text, nullable=True)
    sentiment = Column(SAEnum(SentimentType), nullable=True)

    source = Column(SAEnum(SourceType), nullable=False, default=SourceType.form)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    rep = relationship("Rep", back_populates="interactions")
    hcp = relationship("HCP", back_populates="interactions")