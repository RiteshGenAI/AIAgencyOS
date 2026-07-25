"""Password reset tests."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def _unique_email(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}@example.com"


def test_forgot_password_returns_generic_message(client: TestClient):
    email = _unique_email("reset")
    client.post(
        "/api/v1/auth/signup",
        json={
            "tenant_id": "tenant-1",
            "email": email,
            "password": "password123!",
            "role": "owner",
        },
    )
    resp = client.post("/api/v1/auth/forgot-password", json={"email": email})
    assert resp.status_code == 200
    assert resp.json()["message"] == "If an account exists, a reset link has been sent."


def test_forgot_password_for_unknown_email_is_silent(client: TestClient):
    resp = client.post("/api/v1/auth/forgot-password", json={"email": "noone@example.com"})
    assert resp.status_code == 200
    assert resp.json()["message"] == "If an account exists, a reset link has been sent."


def test_reset_password_service_happy_path(db_session: Session):
    from backend.app.services.auth_service import create_user, confirm_password_reset
    from backend.app.core.config import Role
    from backend.app.schemas.user_schema import SignupRequest
    from backend.app.models.password_reset_token import PasswordResetToken
    import secrets

    email = _unique_email("reset-svc")
    user = create_user(
        db_session,
        SignupRequest(tenant_id="tenant-1", email=email, password="password123!", role=Role.OWNER),
    )
    db_session.commit()

    raw_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
    reset = PasswordResetToken(
        id=str(uuid.uuid4()),
        user_id=user.id,
        token_hash=__import__("backend.app.services.auth_service", fromlist=["_hash_token"])._hash_token(raw_token),
        expires_at=expires_at,
        used=False,
    )
    db_session.add(reset)
    db_session.commit()

    assert reset.used is False

    confirm_password_reset(db_session, raw_token, "newPass1!")
    db_session.commit()

    db_session.refresh(reset)
    assert reset.used is True

    from backend.app.services.auth_service import authenticate_user
    authenticated = authenticate_user(db_session, email, "newPass1!")
    assert authenticated is not None


def test_reset_password_with_invalid_token(db_session: Session):
    from backend.app.services.auth_service import confirm_password_reset
    with pytest.raises(__import__("fastapi").HTTPException) as exc_info:
        confirm_password_reset(db_session, "invalid-token", "newPass1!")
    assert exc_info.value.status_code == 400


def test_reset_password_with_weak_password_via_api(client: TestClient, db_session: Session):
    from backend.app.services.auth_service import create_user, request_password_reset
    from backend.app.schemas.user_schema import SignupRequest
    from backend.app.core.config import Role
    from backend.app.models.password_reset_token import PasswordResetToken

    email = _unique_email("reset-weak-api")
    user = create_user(
        db_session,
        SignupRequest(tenant_id="tenant-1", email=email, password="password123!", role=Role.MEMBER),
    )
    db_session.commit()

    request_password_reset(db_session, email)
    db_session.commit()

    token_row = db_session.query(PasswordResetToken).filter(PasswordResetToken.user_id == user.id).first()
    assert token_row is not None

    resp = client.post("/api/v1/auth/reset-password", json={"token": token_row.token_hash, "new_password": "short"})
    assert resp.status_code == 422
