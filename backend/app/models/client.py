from datetime import datetime, timezone

from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from backend.app.db.session import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    name = Column(String, nullable=False)
    contact_email = Column(String, nullable=True)
    reference_id = Column(String, nullable=False, index=True)  # human-readable ID like CID-0001
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    tenant = relationship("Tenant")
