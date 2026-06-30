from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from backend.app.db.session import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    client_id = Column(String, ForeignKey("clients.id"), nullable=True)

    source = Column(String, nullable=True)
    raw_text = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="new")

    tenant = relationship("Tenant")
    client = relationship("Client")
