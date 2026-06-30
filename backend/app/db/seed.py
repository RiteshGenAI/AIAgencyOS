import logging
import os
import uuid

from backend.app.db.session import SessionLocal
from backend.app.models.user import User
from backend.app.services.auth_service import get_password_hash

logger = logging.getLogger(__name__)

ADMIN_EMAIL = os.getenv("BACKEND_SEED_ADMIN_EMAIL", "admin@agency.local")
ADMIN_PASSWORD = os.getenv("BACKEND_SEED_ADMIN_PASSWORD", "admin1234")
ADMIN_TENANT_ID = os.getenv("BACKEND_SEED_ADMIN_TENANT_ID", "default")


def seed_admin_user() -> None:
    """Create the default admin user if no users exist and seeding is enabled.

    This is intended for local / first-time bootstrapping only. In production,
    set BACKEND_SEED_ADMIN=false and create the first user via the signup API
    or a secure external process.
    """
    seed_enabled = os.getenv("BACKEND_SEED_ADMIN", "false").lower() in ("true", "1", "yes")
    if not seed_enabled:
        return

    db = SessionLocal()
    try:
        existing = db.query(User).first()
        if existing:
            logger.info("Database already contains users; skipping admin seed.")
            return

        admin = User(
            id=str(uuid.uuid4()),
            tenant_id=ADMIN_TENANT_ID,
            email=ADMIN_EMAIL.lower().strip(),
            hashed_password=get_password_hash(ADMIN_PASSWORD),
            role="owner",
            is_active=True,
        )
        db.add(admin)
        db.commit()
        logger.info("Seeded admin user %s", ADMIN_EMAIL)
    finally:
        db.close()
