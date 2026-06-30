import uuid
from sqlalchemy.orm import Session

from backend.app.models.lead import Lead
from backend.app.schemas.lead_schema import LeadCreate, LeadRead


def create_lead(db: Session, lead_in: LeadCreate) -> LeadRead:
    lead = Lead(
        id=str(uuid.uuid4()),
        tenant_id=lead_in.tenant_id,
        client_id=lead_in.client_id,
        source=lead_in.source,
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
