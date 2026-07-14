"""
Interaction router.

Implements the mandatory API surface:
    POST /interaction        - create (Form Mode submission)
    PUT  /interaction/{id}   - update (Edit Interaction path)
    GET  /interaction        - list/search (Dashboard + Search tool)
    GET  /interaction/{id}   - fetch single record

Routers stay thin — all business logic lives in
app.services.interaction_service, which is also what the LangGraph
tools call into, so the REST API and the AI agent share one code path.
"""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.interaction import InteractionCreate, InteractionOut, InteractionUpdate
from app.services import interaction_service

router = APIRouter(prefix="/interaction", tags=["Interaction"])


@router.post("", response_model=InteractionOut, status_code=201)
def create_interaction(payload: InteractionCreate, db: Session = Depends(get_db)):
    """Creates a new interaction record (Form Mode path)."""
    return interaction_service.create_interaction(db, payload)


@router.get("", response_model=List[InteractionOut])
def list_interactions(
    q: Optional[str] = None,
    hcp_name: Optional[str] = None,
    hospital: Optional[str] = None,
    product: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    rep_id: Optional[int] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Lists/searches interactions. Supports either a loose free-text
    query (`q`) or specific filters — used by both the Dashboard
    search box and the Search Interaction LangGraph tool.
    """
    return interaction_service.list_interactions(
        db,
        q=q,
        hcp_name=hcp_name,
        hospital=hospital,
        product=product,
        date_from=date_from,
        date_to=date_to,
        rep_id=rep_id,
        limit=limit,
    )


@router.get("/{interaction_id}", response_model=InteractionOut)
def get_interaction(interaction_id: int, db: Session = Depends(get_db)):
    interaction = interaction_service.get_interaction(db, interaction_id)
    if not interaction:
        raise HTTPException(status_code=404, detail=f"Interaction {interaction_id} not found")
    return interaction


@router.put("/{interaction_id}", response_model=InteractionOut)
def update_interaction(
    interaction_id: int, payload: InteractionUpdate, db: Session = Depends(get_db)
):
    """Applies a partial update to an existing interaction (Edit Interaction path)."""
    interaction = interaction_service.update_interaction(db, interaction_id, payload)
    if not interaction:
        raise HTTPException(status_code=404, detail=f"Interaction {interaction_id} not found")
    return interaction