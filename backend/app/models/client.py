from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from backend.app.db.session import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    name = Column(String, nullable=False)
    contact_email = Column(String, nullable=True)

    tenant = relationship("Tenant")
