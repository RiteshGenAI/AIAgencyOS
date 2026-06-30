from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from backend.app.core.config import Role, settings
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.user_schema import TokenPayload


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Decode JWT and fetch current user.

    Raises 401 if token invalid, 404 if user not found.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        token_data = TokenPayload(**payload)
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == token_data.sub).first()
    if not user or not user.is_active:
        raise credentials_exception

    return user


def ensure_tenant(user: User, tenant_id: str) -> None:
    if user.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant mismatch")


# ---------------------------------------------------------------------------
# RBAC dependencies (adapted from Sentinel's require_roles / require_admin).
# ---------------------------------------------------------------------------


def require_roles(*allowed_roles: Role):
    """Build a FastAPI dependency that allows only the listed roles.

    Usage::

        @router.post("/", dependencies=[Depends(require_roles(Role.OWNER, Role.MANAGER))])
    """

    allowed = {r.value for r in allowed_roles}

    def _checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return _checker


def require_admin():
    """Dependency factory: only users with the OWNER role may proceed."""

    return require_roles(Role.OWNER)

