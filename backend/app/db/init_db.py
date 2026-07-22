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


def _generate_next_client_reference_id(conn, tenant_id: str) -> str:
    """Return the next available CID-XXXX reference ID for a tenant."""
    row = conn.execute(
        text(
            "SELECT reference_id FROM clients "
            "WHERE tenant_id = :tenant_id AND reference_id LIKE 'CID-%' "
            "ORDER BY reference_id DESC LIMIT 1"
        ),
        {"tenant_id": tenant_id},
    ).fetchone()
    if row and row[0]:
        try:
            num = int(row[0].split("-")[-1]) + 1
        except (ValueError, IndexError):
            num = 1
    else:
        num = 1
    return f"CID-{num:04d}"


def _run_migrations():
    migrations = [
        "ALTER TABLE projects ADD COLUMN IF NOT EXISTS scoped_summary TEXT",
        "ALTER TABLE clients ADD COLUMN IF NOT EXISTS reference_id VARCHAR",
    ]
    with engine.connect() as conn:
        for sql in migrations:
            try:
                conn.execute(text(sql))
                conn.commit()
            except Exception as exc:
                logger.warning("Migration skipped: %s", exc)

        # Backfill reference_id for existing clients that do not have one.
        try:
            rows = conn.execute(
                text("SELECT id, tenant_id FROM clients WHERE reference_id IS NULL")
            ).fetchall()
            for client_id, tenant_id in rows:
                ref = _generate_next_client_reference_id(conn, tenant_id)
                conn.execute(
                    text("UPDATE clients SET reference_id = :ref WHERE id = :id"),
                    {"ref": ref, "id": client_id},
                )
            if rows:
                conn.commit()
                logger.info("Backfilled reference_id for %s client(s)", len(rows))
        except Exception as exc:
            logger.warning("Client reference_id backfill skipped: %s", exc)

        # Add a unique index for (tenant_id, reference_id) to prevent duplicates.
        try:
            conn.execute(
                text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS idx_clients_tenant_reference "
                    "ON clients (tenant_id, reference_id)"
                )
            )
            conn.commit()
        except Exception as exc:
            logger.warning("Client reference_id unique index skipped: %s", exc)

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
