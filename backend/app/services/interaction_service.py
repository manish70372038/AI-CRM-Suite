"""
Interaction service layer.

Centralizes all database operations for Interaction records. Both the
FastAPI routers (routers/interaction.py) and the LangGraph tools
(agent/tools/log_interaction.py, edit_interaction.py, etc.) call into
this module rather than touching the ORM directly — this guarantees
the REST API and the AI agent always produce/see data the same way.
"""

from datetime import date
from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.interaction import Interaction
from app.schemas.interaction import InteractionCreate, InteractionUpdate
from app.services.hcp_resolver import resolve_or_create_hcp


def create_interaction(db: Session, data: InteractionCreate) -> Interaction:
    """
    Creates a new interaction. If hcp_id isn't already provided, this
    attempts to resolve/create an HCP record from doctor_name/hospital
    so the interaction is linked for future search/summarize calls.
    """
    hcp_id = data.hcp_id
    if hcp_id is None:
        hcp = resolve_or_create_hcp(db, data.doctor_name, data.hospital)
        hcp_id = hcp.id if hcp else None

    interaction = Interaction(
        rep_id=data.rep_id,
        hcp_id=hcp_id,
        doctor_name=data.doctor_name,
        hospital=data.hospital,
        interaction_type=data.interaction_type,
        products_discussed=data.products_discussed,
        summary=data.summary,
        raw_notes=data.raw_notes,
        follow_up_date=data.follow_up_date,
        follow_up_action=data.follow_up_action,
        sentiment=data.sentiment,
        source=data.source,
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction


def get_interaction(db: Session, interaction_id: int) -> Optional[Interaction]:
    return db.query(Interaction).filter(Interaction.id == interaction_id).first()


def update_interaction(
    db: Session, interaction_id: int, data: InteractionUpdate
) -> Optional[Interaction]:
    """
    Applies a partial update. Only fields explicitly set on `data`
    (i.e. not None/unset) are written, so callers can update a single
    field — such as just follow_up_date — without clobbering the rest.
    """
    interaction = get_interaction(db, interaction_id)
    if not interaction:
        return None

    update_fields = data.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in update_fields.items():
        setattr(interaction, field, value)

    db.commit()
    db.refresh(interaction)
    return interaction


def list_interactions(
    db: Session,
    q: Optional[str] = None,
    hcp_name: Optional[str] = None,
    hospital: Optional[str] = None,
    product: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    rep_id: Optional[int] = None,
    limit: int = 100,
) -> List[Interaction]:
    """
    Flexible search used by both GET /interaction (dashboard/search box)
    and the Search Interaction tool. `q` performs a loose substring
    match across doctor_name, hospital, and summary as a fallback when
    no specific filter fields are supplied.
    """
    query = db.query(Interaction)

    if rep_id is not None:
        query = query.filter(Interaction.rep_id == rep_id)

    if hcp_name:
        query = query.filter(Interaction.doctor_name.ilike(f"%{hcp_name}%"))

    if hospital:
        query = query.filter(Interaction.hospital.ilike(f"%{hospital}%"))

    if product:
        # products_discussed is a JSON array column; cast to text for a
        # simple substring search (sufficient at this scale).
        query = query.filter(Interaction.products_discussed.cast(str).ilike(f"%{product}%"))

    if date_from:
        query = query.filter(Interaction.created_at >= date_from)

    if date_to:
        query = query.filter(Interaction.created_at <= date_to)

    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Interaction.doctor_name.ilike(like),
                Interaction.hospital.ilike(like),
                Interaction.summary.ilike(like),
                Interaction.raw_notes.ilike(like),
            )
        )

    return query.order_by(Interaction.created_at.desc()).limit(limit).all()


def get_interactions_for_hcp(
    db: Session, hcp_id: Optional[int] = None, doctor_name: Optional[str] = None, limit: int = 20
) -> List[Interaction]:
    """
    Fetches interaction history for a given HCP, used by the
    Summarize Previous Interactions tool. Falls back to matching by
    doctor_name if hcp_id isn't known/resolved.
    """
    query = db.query(Interaction)

    if hcp_id is not None:
        query = query.filter(Interaction.hcp_id == hcp_id)
    elif doctor_name:
        query = query.filter(Interaction.doctor_name.ilike(f"%{doctor_name}%"))
    else:
        return []

    return query.order_by(Interaction.created_at.desc()).limit(limit).all()