"""Admin endpoints for user and RBAC management.

Adapted from Sentinel's admin router. Restricted to OWNER role.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.core.config import Role
from backend.app.core.security import get_current_user
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.user_schema import UserRead
from backend.app.services.auth_service import (
    deactivate_user,
    list_users,
    update_user_role,
)


router = APIRouter(prefix="/admin", tags=["admin"])


def _require_owner(current_user: User = Depends(get_current_user)) -> User:
    """Allow only OWNER role to access admin endpoints."""
    if current_user.role != Role.OWNER.value:
        raise HTTPException(status_code=403, detail="Owner access required")
    return current_user


@router.get("/users", response_model=list[UserRead], dependencies=[Depends(_require_owner)])
def admin_list_users(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    tenant_id: str | None = Query(None, description="Optional tenant scope"),
):
    """List all users (optionally filtered by tenant). Owners only."""
    users = list_users(db, skip=skip, limit=limit, tenant_id=tenant_id)
    return [UserRead.model_validate(u) for u in users]


@router.put(
    "/users/{user_id}/role",
    response_model=UserRead,
    dependencies=[Depends(_require_owner)],
)
def admin_change_role(
    user_id: str,
    new_role: Role,
    db: Session = Depends(get_db),
):
    """Change a user's role. Owners only."""
    user = update_user_role(db, user_id=user_id, new_role=new_role.value)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead.model_validate(user)


@router.delete(
    "/users/{user_id}",
    dependencies=[Depends(_require_owner)],
)
def admin_deactivate_user(user_id: str, db: Session = Depends(get_db)):
    """Soft-deactivate a user. Owners only."""
    ok = deactivate_user(db, user_id=user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
    return {"ok": True}
