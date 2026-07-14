"""
HCP (Healthcare Professional) model.

Fields mirror app.schemas.hcp.HCPOut exactly. Rows are created
implicitly by app.services.hcp_resolver when a Log Interaction tool
call mentions a doctor that doesn't yet have a matching record.
"""

from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from app.database import Base


class HCP(Base):
    __tablename__ = "hcps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    specialization = Column(String(150), nullable=True)
    hospital = Column(String(200), nullable=True)
    phone = Column(String(30), nullable=True)
    email = Column(String(150), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    interactions = relationship("Interaction", back_populates="hcp")