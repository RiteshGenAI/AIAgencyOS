from sqlalchemy import Column, String, Text, Float, ForeignKey
from sqlalchemy.orm import relationship

from backend.app.db.session import Base


class SentinelEvent(Base):
    __tablename__ = "sentinel_events"

    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, nullable=False, index=True)
    entity_type = Column(String, nullable=False)  # lead | project | workflow
    entity_id = Column(String, nullable=False)

    scan_type = Column(String, nullable=False)  # prompt | output | tool_call
    risk_score = Column(Float, nullable=False)
    issues = Column(Text, nullable=True)

    # optional foreign key to project
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)

    project = relationship("Project")
