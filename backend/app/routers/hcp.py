"""
HCP router.

Exposes a single read endpoint used by the frontend's Form Mode
autocomplete. HCP creation is handled implicitly by the Log
Interaction tool via hcp_resolver — no POST endpoint is needed here
for this assignment's scope.
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.hcp import HCP
from app.schemas.hcp import HCPOut

router = APIRouter(prefix="/hcp", tags=["HCP"])


@router.get("", response_model=List[HCPOut])
def list_hcps(db: Session = Depends(get_db)):
    """Returns all known HCPs, most recently added first."""
    return db.query(HCP).order_by(HCP.created_at.desc()).all()