from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from backend.app.db.session import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    client_id = Column(String, ForeignKey("clients.id"), nullable=True)

    source = Column(String, nullable=True)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    raw_text = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="new")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    tenant = relationship("Tenant")
    client = relationship("Client")
