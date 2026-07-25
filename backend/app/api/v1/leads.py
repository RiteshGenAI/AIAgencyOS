from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.config import Role
from backend.app.core.security import get_db, get_current_user, ensure_tenant, require_roles
from backend.app.models.user import User
from backend.app.schemas.lead_schema import LeadCreate, LeadRead
from backend.app.services.lead_service import create_lead, list_leads


router = APIRouter(prefix="/leads", tags=["leads"])


@router.post(
    "/",
    response_model=LeadRead,
    dependencies=[Depends(require_roles(Role.OWNER, Role.MANAGER, Role.MEMBER))],
)
async def create_lead_endpoint(
    lead_in: LeadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LeadRead:
    ensure_tenant(current_user, lead_in.tenant_id)
    return create_lead(db, lead_in)


@router.get(
    "/{tenant_id}",
    response_model=list[LeadRead],
    dependencies=[Depends(require_roles(Role.OWNER, Role.MANAGER, Role.MEMBER, Role.CLIENT))],
)
async def list_leads_endpoint(
    tenant_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> list[LeadRead]:
    ensure_tenant(current_user, tenant_id)
    return list_leads(db, tenant_id, skip=skip, limit=limit)
