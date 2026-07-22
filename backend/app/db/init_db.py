import logging

from sqlalchemy import text

from backend.app.db.session import Base, engine
from backend.app.models import (  # noqa: F401
    tenant,
    client,
    lead,
    project,
    user,
    sentinel_event,
    invoice,
)

logger = logging.getLogger(__name__)


def _run_migrations():
    migrations = [
        "ALTER TABLE projects ADD COLUMN IF NOT EXISTS scoped_summary TEXT",
    ]
    with engine.connect() as conn:
        for sql in migrations:
            try:
                conn.execute(text(sql))
                conn.commit()
            except Exception as exc:
                logger.warning("Migration skipped: %s", exc)

        # Normalize legacy "admin" role to "owner". The current RBAC model only
        # recognizes owner/manager/member/client, so any leftover "admin" role
        # causes every protected endpoint to return 403.
        try:
            result = conn.execute(
                text("UPDATE users SET role = 'owner' WHERE role = 'admin'")
            )
            conn.commit()
            if result.rowcount:
                logger.info("Migrated %s user(s) from role 'admin' to 'owner'", result.rowcount)
        except Exception as exc:
            logger.warning("Admin role migration skipped: %s", exc)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    try:
        _run_migrations()
    except Exception as exc:
        logger.warning("Migrations could not run: %s", exc)
