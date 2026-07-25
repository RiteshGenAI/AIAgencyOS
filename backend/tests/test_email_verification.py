"""Email verification tests."""
from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def _unique_email(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}@example.com"


def test_signup_creates_unverified_user(client: TestClient):
    email = _unique_email("verify")
    resp = client.post(
        "/api/v1/auth/signup",
        json={
            "tenant_id": "tenant-1",
            "email": email,
            "password": "password123!",
            "role": "member",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["is_verified"] is False


def test_verify_email_service_happy_path(db_session: Session):
    from backend.app.services.auth_service import verify_email
    from backend.app.models.user import User
    from backend.app.core.config import Role
    from backend.app.services.auth_service import get_password_hash
    import secrets

    raw_token = secrets.token_urlsafe(32)
    user = User(
        id=str(uuid.uuid4()),
        tenant_id="tenant-1",
        email=_unique_email("verify-svc"),
        hashed_password=get_password_hash("password123!"),
        role=Role.MEMBER,
        is_active=True,
        verification_token_hash=__import__("backend.app.services.auth_service", fromlist=["_hash_token"])._hash_token(raw_token),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.is_verified is False
    verify_email(db_session, raw_token)
    db_session.commit()

    db_session.refresh(user)
    assert user.is_verified is True


def test_verify_email_with_invalid_token(db_session: Session):
    from backend.app.services.auth_service import verify_email
    with pytest.raises(__import__("fastapi").HTTPException) as exc_info:
        verify_email(db_session, "invalid-token")
    assert exc_info.value.status_code == 400


def test_unverified_user_can_login_when_flag_off(client: TestClient):
    email = _unique_email("verify3")
    resp = client.post(
        "/api/v1/auth/signup",
        json={
            "tenant_id": "tenant-1",
            "email": email,
            "password": "password123!",
            "role": "member",
        },
    )
    assert resp.status_code == 200

    login = client.post("/api/v1/auth/login", json={"email": email, "password": "password123!"})
    assert login.status_code == 200
