from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from backend.app.db.session import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)

    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="draft")

    # simple JSON/text field for scoped summary (for demo purposes)
    scoped_summary = Column(Text, nullable=True)

    tenant = relationship("Tenant")
    client = relationship("Client")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
