"""General API tests: health, auth flow, and route smoke checks.

All tests run against a real PostgreSQL test database (see ``conftest.py``).
SQLite and any other non-PostgreSQL database are forbidden by policy.
"""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient


def _unique_email(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}@example.com"


def test_healthz(client: TestClient):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_db(client: TestClient):
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    assert response.json()["database"] == "ok"


def test_signup_and_login(client: TestClient):
    email = _unique_email("signup")
    signup = client.post(
        "/api/v1/auth/signup",
        json={
            "tenant_id": "tenant-1",
            "email": email,
            "password": "password123",
            "role": "owner",
        },
    )
    assert signup.status_code == 200
    assert signup.json()["email"] == email
    assert signup.json()["role"] == "owner"

    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "password123"},
    )
    assert login.status_code == 200
    data = login.json()
    assert "access_token" in data
    assert data["user"] == {
        "id": signup.json()["id"],
        "tenant_id": "tenant-1",
        "email": email,
        "role": "owner",
    }


def test_signup_defaults_to_member_when_role_omitted(client: TestClient):
    email = _unique_email("default")
    signup = client.post(
        "/api/v1/auth/signup",
        json={
            "tenant_id": "tenant-1",
            "email": email,
            "password": "password123",
        },
    )
    assert signup.status_code == 200
    assert signup.json()["role"] == "member"


def test_login_invalid(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nope@example.com", "password": "wrong"},
    )
    assert response.status_code == 401


def test_signup_duplicate_email(client: TestClient):
    email = _unique_email("dup")
    body = {
        "tenant_id": "tenant-1",
        "email": email,
        "password": "password123",
    }
    first = client.post("/api/v1/auth/signup", json=body)
    assert first.status_code == 200
    second = client.post("/api/v1/auth/signup", json=body)
    assert second.status_code == 400
    assert "already registered" in second.json()["detail"]


def test_projects_require_auth(client: TestClient):
    response = client.get("/api/v1/projects/demo-tenant")
    assert response.status_code == 401


def test_create_invoice_missing_project(client: TestClient, auth_headers):
    headers = auth_headers(_unique_email("inv"), role="member")
    resp = client.post(
        "/api/v1/invoices/",
        json={
            "tenant_id": "tenant-1",
            "project_id": "nonexistent",
            "amount": 100.0,
            "currency": "USD",
        },
        headers=headers,
    )
    assert resp.status_code == 404


def test_internal_sentinel_scan(client: TestClient):
    response = client.post(
        "/internal/sentinel/scan",
        json={
            "payload": "hello",
            "policy_id": "default",
            "scan_type": "prompt",
        },
    )
    assert response.status_code == 200
    assert response.json()["allowed"] is True
