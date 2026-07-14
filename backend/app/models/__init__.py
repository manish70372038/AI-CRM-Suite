"""
Aggregates all ORM models so a single `import app.models` registers
every table on Base.metadata — required by Alembic autogenerate and
by Base.metadata.create_all() during local/dev bootstrapping.
"""

from app.database import Base
from app.models.rep import Rep
from app.models.hcp import HCP
from app.models.interaction import Interaction, InteractionType, SentimentType, SourceType
from app.models.chat import ChatSession, ChatMessage

__all__ = [
    "Base",
    "Rep",
    "HCP",
    "Interaction",
    "InteractionType",
    "SentimentType",
    "SourceType",
    "ChatSession",
    "ChatMessage",
]