from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from backend.app.db.session import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, nullable=False, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)

    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    status = Column(String, default="draft")  # draft | sent | paid | cancelled

    project = relationship("Project")
