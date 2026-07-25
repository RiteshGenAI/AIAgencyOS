import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import HTTPException
from jose import jwt
from sqlalchemy.orm import Session

from backend.app.core.config import Role, settings
from backend.app.models.tenant import Tenant
from backend.app.models.user import User
from backend.app.models.password_reset_token import PasswordResetToken
from backend.app.schemas.user_schema import SignupRequest, Token, UserRead, UserSession


ALGORITHM = "HS256"
RESET_TOKEN_EXPIRE_MINUTES = 15
VERIFICATION_TOKEN_EXPIRE_MINUTES = 60


class LastActiveOwnerError(ValueError):
    """Raised when an operation would leave no active owner."""


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_user(db: Session, user_in: SignupRequest) -> UserRead:
    """Create a public signup user using the role supplied by the client."""
    existing = db.query(User).filter(User.email == user_in.email.strip().lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    tenant = db.query(Tenant).filter(Tenant.id == user_in.tenant_id).first()
    if not tenant:
        tenant = Tenant(id=user_in.tenant_id, name=f"Tenant {user_in.tenant_id}")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

    verification_token = secrets.token_urlsafe(32)

    user = User(
        id=str(uuid.uuid4()),
        tenant_id=user_in.tenant_id,
        email=user_in.email.strip().lower(),
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role,
        verification_token_hash=_hash_token(verification_token),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    _log_stub_email(
        to=user.email,
        subject="Verify your email",
        body=f"Welcome! Verify your email: /api/v1/auth/verify-email?token={verification_token}",
    )

    return UserRead.model_validate(user)


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email.strip().lower()).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
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
    return Token(access_token=encoded_jwt, user=UserSession.model_validate(user))


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
    return q.order_by(User.created_at.desc()).offset(skip).limit(limit).all()


def _is_last_active_owner(db: Session, user: User) -> bool:
    return (
        user.is_active
        and user.role == Role.OWNER.value
        and db.query(User)
        .filter(User.is_active.is_(True), User.role == Role.OWNER.value)
        .count()
        <= 1
    )


def update_user_role(db: Session, *, user_id: str, new_role: str) -> User | None:
    """Change a user's role. Returns the updated user, or None if not found."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    if new_role != Role.OWNER.value and _is_last_active_owner(db, user):
        raise LastActiveOwnerError("Cannot remove the last active owner")
    user.role = new_role
    db.commit()
    db.refresh(user)
    return user


def deactivate_user(db: Session, *, user_id: str) -> bool:
    """Soft-deactivate a user by flipping ``is_active`` to False."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    if _is_last_active_owner(db, user):
        raise LastActiveOwnerError("Cannot deactivate the last active owner")
    user.is_active = False
    db.commit()
    return True


# ---------------------------------------------------------------------------
# Password reset
# ---------------------------------------------------------------------------


def request_password_reset(db: Session, email: str) -> None:
    user = db.query(User).filter(User.email == email.strip().lower()).first()
    if not user:
        return
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    reset = PasswordResetToken(
        id=str(uuid.uuid4()),
        user_id=user.id,
        token_hash=_hash_token(token),
        expires_at=expires_at,
    )
    db.add(reset)
    db.commit()
    _log_stub_email(
        to=user.email,
        subject="Reset your password",
        body=f"Reset your password: /api/v1/auth/reset-password?token={token}",
    )


def confirm_password_reset(db: Session, token: str, new_password: str) -> None:
    token_hash = _hash_token(token)
    reset = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token_hash == token_hash, PasswordResetToken.used.is_(False))
        .first()
    )
    if not reset:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    if reset.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == reset.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user.hashed_password = get_password_hash(new_password)
    reset.used = True
    db.commit()


# ---------------------------------------------------------------------------
# Email verification
# ---------------------------------------------------------------------------


def verify_email(db: Session, token: str) -> None:
    token_hash = _hash_token(token)
    user = db.query(User).filter(User.verification_token_hash == token_hash).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification token")
    user.is_verified = True
    user.verification_token_hash = None
    db.commit()


def _log_stub_email(to: str, subject: str, body: str) -> None:
    import logging
    logger = logging.getLogger("email")
    logger.info("STUB EMAIL to=%s subject=%s body=%s", to, subject, body)
