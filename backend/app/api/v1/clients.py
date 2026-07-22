from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.security import get_db, get_current_user, ensure_tenant, require_roles
from backend.app.core.config import Role
from backend.app.models.user import User
from backend.app.schemas.client_schema import ClientCreate, ClientRead
from backend.app.services.client_service import create_client, list_clients


router = APIRouter(prefix="/clients", tags=["clients"])


@router.post(
    "/",
    response_model=ClientRead,
    dependencies=[Depends(require_roles(Role.OWNER, Role.MANAGER))],
)
async def create_client_endpoint(
    client_in: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClientRead:
    ensure_tenant(current_user, client_in.tenant_id)
    try:
        return create_client(db, client_in)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get(
    "/{tenant_id}",
    response_model=list[ClientRead],
    dependencies=[Depends(require_roles(Role.OWNER, Role.MANAGER, Role.MEMBER, Role.CLIENT))],
)
async def list_clients_endpoint(
    tenant_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ClientRead]:
    ensure_tenant(current_user, tenant_id)
    return list_clients(db, tenant_id)
