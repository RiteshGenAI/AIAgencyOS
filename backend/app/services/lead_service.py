import uuid
from sqlalchemy.orm import Session

from backend.app.models.client import Client
from backend.app.models.lead import Lead
from backend.app.schemas.lead_schema import LeadCreate, LeadRead


def _resolve_client_id(db: Session, tenant_id: str, client_id: str | None) -> str | None:
    if not client_id:
        return None
    client = db.query(Client).filter(Client.id == client_id).first()
    if client:
        return client.id
    client = db.query(Client).filter(Client.tenant_id == tenant_id, Client.reference_id == client_id).first()
    if client:
        return client.id
    raise ValueError(f"Client '{client_id}' not found")


def create_lead(db: Session, lead_in: LeadCreate) -> LeadRead:
    resolved_client_id = _resolve_client_id(db, lead_in.tenant_id, lead_in.client_id)
    lead = Lead(
        id=str(uuid.uuid4()),
        tenant_id=lead_in.tenant_id,
        client_id=resolved_client_id,
        source=lead_in.source,
        name=lead_in.name,
        email=lead_in.email,
        phone=lead_in.phone,
        notes=lead_in.notes,
        raw_text=lead_in.raw_text,
        status="new",
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return LeadRead.model_validate(lead)


def list_leads(db: Session, tenant_id: str) -> list[LeadRead]:
    q = db.query(Lead).filter(Lead.tenant_id == tenant_id)
    return [LeadRead.model_validate(x) for x in q.all()]
