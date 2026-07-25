import uuid
from sqlalchemy.orm import Session

from backend.app.models.client import Client
from backend.app.models.tenant import Tenant
from backend.app.schemas.client_schema import ClientCreate, ClientRead


def _generate_next_client_reference_id(db: Session, tenant_id: str) -> str:
    """Return the next available CID-XXXX reference ID for a tenant."""
    row = (
        db.query(Client.reference_id)
        .filter(Client.tenant_id == tenant_id, Client.reference_id.like("CID-%"))
        .order_by(Client.reference_id.desc())
        .first()
    )
    if row and row[0]:
        try:
            num = int(row[0].split("-")[-1]) + 1
        except (ValueError, IndexError):
            num = 1
    else:
        num = 1
    return f"CID-{num:04d}"


def create_client(db: Session, client_in: ClientCreate) -> ClientRead:
    tenant = db.query(Tenant).filter(Tenant.id == client_in.tenant_id).first()
    if not tenant:
        raise ValueError("Tenant not found")

    reference_id = client_in.reference_id
    if not reference_id:
        reference_id = _generate_next_client_reference_id(db, client_in.tenant_id)
        # Ensure uniqueness even with race conditions
        while db.query(Client).filter(Client.tenant_id == client_in.tenant_id, Client.reference_id == reference_id).first():
            num = int(reference_id.split("-")[-1]) + 1
            reference_id = f"CID-{num:04d}"
    else:
        existing = (
            db.query(Client)
            .filter(Client.tenant_id == client_in.tenant_id, Client.reference_id == reference_id)
            .first()
        )
        if existing:
            raise ValueError(f"Client reference_id '{reference_id}' already exists for this tenant")

    client = Client(
        id=str(uuid.uuid4()),
        tenant_id=client_in.tenant_id,
        name=client_in.name,
        contact_email=client_in.contact_email,
        reference_id=reference_id,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return ClientRead.model_validate(client)


def list_clients(db: Session, tenant_id: str, skip: int = 0, limit: int = 100) -> list[ClientRead]:
    q = db.query(Client).filter(Client.tenant_id == tenant_id)
    return [ClientRead.model_validate(c) for c in q.offset(skip).limit(limit).all()]


def get_client_by_reference(db: Session, tenant_id: str, reference_id: str) -> Client | None:
    return (
        db.query(Client)
        .filter(Client.tenant_id == tenant_id, Client.reference_id == reference_id)
        .first()
    )
