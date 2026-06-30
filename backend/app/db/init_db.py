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


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    try:
        _run_migrations()
    except Exception as exc:
        logger.warning("Migrations could not run: %s", exc)
