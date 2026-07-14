"""
Pydantic schemas for Healthcare Professional (HCP) data.

Only a read schema is needed for this assignment's scope — HCPs are
created implicitly by the Log Interaction tool (via hcp_resolver),
not through a dedicated create endpoint.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class HCPOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    specialization: Optional[str] = None
    hospital: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    created_at: datetime