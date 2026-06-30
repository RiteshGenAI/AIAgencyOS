import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import HTTPException
from jose import jwt
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models.user import User
from backend.app.schemas.user_schema import UserCreate, UserRead, Token

ALGORITHM = "HS256"


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_user(db: Session, user_in: UserCreate) -> UserRead:
    existing = db.query(User).filter(User.email == user_in.email.strip().lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        id=str(uuid.uuid4()),
        tenant_id=user_in.tenant_id,
        email=user_in.email.strip().lower(),
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserRead.model_validate(user)


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email.strip().lower()).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(*, user: User, expires_delta: timedelta | None = None) -> Token:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {
        "sub": user.id,
        "tenant_id": user.tenant_id,
        "role": user.role,
        "exp": expire,
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return Token(access_token=encoded_jwt)


# ---------------------------------------------------------------------------
# Admin / RBAC management services (adapted from Sentinel's auth_service).
# ---------------------------------------------------------------------------


def list_users(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    tenant_id: str | None = None,
) -> list[User]:
    """List users, optionally scoped to a single tenant."""
    q = db.query(User)
    if tenant_id is not None:
        q = q.filter(User.tenant_id == tenant_id)
    return q.order_by(User.created_at.desc() if hasattr(User, "created_at") else User.email).offset(skip).limit(limit).all()


def update_user_role(db: Session, *, user_id: str, new_role: str) -> User | None:
    """Change a user's role. Returns the updated user, or None if not found."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    user.role = new_role
    db.commit()
    db.refresh(user)
    return user


def deactivate_user(db: Session, *, user_id: str) -> bool:
    """Soft-deactivate a user by flipping ``is_active`` to False."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    user.is_active = False
    db.commit()
    return True
