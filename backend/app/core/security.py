from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from backend.app.core.config import Role, settings
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.user_schema import TokenPayload


# Use HTTPBearer (not OAuth2PasswordBearer) because the /auth/login endpoint
# accepts a JSON body (`{"email", "password"}`) rather than the OAuth2 form
# flow (`username` + `password`). HTTPBearer makes Swagger UI show a simple
# "Bearer token" dialog instead of trying to call /login with form data.
oauth2_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Decode JWT and fetch current user.

    Raises 401 if token invalid or user not found.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if creds is None or not creds.credentials:
        raise credentials_exception

    try:
        payload = jwt.decode(creds.credentials, settings.SECRET_KEY, algorithms=["HS256"])
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

