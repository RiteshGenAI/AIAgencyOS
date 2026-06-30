import uuid
from sqlalchemy.orm import Session

from backend.app.models.invoice import Invoice
from backend.app.schemas.invoice_schema import InvoiceCreate, InvoiceRead


def create_invoice(db: Session, invoice_in: InvoiceCreate) -> InvoiceRead:
    invoice = Invoice(
        id=str(uuid.uuid4()),
        tenant_id=invoice_in.tenant_id,
        project_id=invoice_in.project_id,
        amount=invoice_in.amount,
        currency=invoice_in.currency,
        status="draft",
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return InvoiceRead.model_validate(invoice)


def list_invoices_for_project(db: Session, project_id: str) -> list[InvoiceRead]:
    q = db.query(Invoice).filter(Invoice.project_id == project_id)
    return [InvoiceRead.model_validate(x) for x in q.all()]
