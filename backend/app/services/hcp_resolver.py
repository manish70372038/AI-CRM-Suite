"""
HCP resolver service.

When the Log Interaction tool extracts a doctor name (and possibly a
hospital) from free text, we don't know upfront whether that HCP
already exists in the database. This service:

1. Searches for existing HCPs whose name is a close match (using
   difflib, no extra fuzzy-matching dependency required).
2. If a confident match is found (similarity above threshold, and
   hospital matches when both are known), returns that HCP's id.
3. Otherwise, creates a new HCP row so future interactions with the
   same doctor can be resolved and linked together.

This keeps `doctor_name`/`hospital` on the Interaction row as the
verbatim source of truth, while `hcp_id` is a best-effort link.
"""

import difflib
from typing import Optional

from sqlalchemy.orm import Session

from app.models.hcp import HCP

SIMILARITY_THRESHOLD = 0.82


def _normalize(text: str) -> str:
    return text.strip().lower().replace("dr.", "").replace("dr ", "").strip()


def find_best_match(db: Session, doctor_name: str, hospital: Optional[str] = None) -> Optional[HCP]:
    """Returns the closest matching HCP row, or None if no confident match exists."""
    if not doctor_name:
        return None

    normalized_target = _normalize(doctor_name)
    candidates = db.query(HCP).all()

    best_match: Optional[HCP] = None
    best_score = 0.0

    for candidate in candidates:
        score = difflib.SequenceMatcher(None, normalized_target, _normalize(candidate.name)).ratio()

        # If both interaction and candidate specify a hospital, require
        # them to reasonably match too — avoids merging two different
        # doctors who happen to share a common name.
        if hospital and candidate.hospital:
            hospital_score = difflib.SequenceMatcher(
                None, hospital.strip().lower(), candidate.hospital.strip().lower()
            ).ratio()
            if hospital_score < 0.6:
                continue

        if score > best_score:
            best_score = score
            best_match = candidate

    if best_match and best_score >= SIMILARITY_THRESHOLD:
        return best_match

    return None


def resolve_or_create_hcp(
    db: Session,
    doctor_name: str,
    hospital: Optional[str] = None,
    specialization: Optional[str] = None,
) -> Optional[HCP]:
    """
    Resolves doctor_name/hospital to an existing HCP row, or creates a
    new one if no confident match is found. Returns None only if
    doctor_name is empty (nothing to resolve).
    """
    if not doctor_name or not doctor_name.strip():
        return None

    existing = find_best_match(db, doctor_name, hospital)
    if existing:
        return existing

    new_hcp = HCP(
        name=doctor_name.strip(),
        hospital=hospital.strip() if hospital else None,
        specialization=specialization,
    )
    db.add(new_hcp)
    db.flush()  # assigns new_hcp.id without committing the outer transaction
    return new_hcp