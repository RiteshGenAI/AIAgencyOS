from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, DateTime

from backend.app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, nullable=False, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="member")  # owner | manager | member | client
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_token_hash = Column(String, nullable=True)
