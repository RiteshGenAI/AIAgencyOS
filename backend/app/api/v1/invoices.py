from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.security import get_db, get_current_user, ensure_tenant
from backend.app.models.user import User
from backend.app.models.project import Project
from backend.app.schemas.invoice_schema import InvoiceCreate, InvoiceRead
from backend.app.services.invoice_service import create_invoice, list_invoices_for_project


router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.post("/", response_model=InvoiceRead)
async def create_invoice_endpoint(
    invoice_in: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InvoiceRead:
    project = db.query(Project).filter(Project.id == invoice_in.project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    ensure_tenant(current_user, project.tenant_id)
    return create_invoice(db, invoice_in)


@router.get("/project/{project_id}", response_model=list[InvoiceRead])
async def list_project_invoices_endpoint(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[InvoiceRead]:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return []
    ensure_tenant(current_user, project.tenant_id)
    return list_invoices_for_project(db, project_id)
