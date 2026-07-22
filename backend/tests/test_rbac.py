"""RBAC tests: require_roles, require_admin, /admin/* endpoints.

Adapted from Sentinel's test suite.

All tests run against a real PostgreSQL test database (see ``conftest.py``).
SQLite and any other non-PostgreSQL database are forbidden by policy.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.main import app
from backend.app.models.user import User
from backend.app.services.auth_service import (
    LastActiveOwnerError,
    deactivate_user,
    get_password_hash,
    update_user_role,
)


def _unique(role: str) -> str:
    """Generate a unique email per test invocation so tests stay isolated."""
    return f"{role}-{uuid.uuid4().hex[:12]}@example.com"


# ---------------------------------------------------------------------------
# /admin/* endpoint access
# ---------------------------------------------------------------------------


def test_admin_users_requires_auth(client: TestClient):
    response = client.get("/api/v1/admin/users")
    assert response.status_code == 401


def test_admin_users_forbidden_for_non_owner(client: TestClient, auth_headers):
    headers = auth_headers(_unique("manager"), role="manager")
    response = client.get("/api/v1/admin/users", headers=headers)
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["detail"] or "Owner" in response.json()["detail"]


def test_admin_users_allowed_for_owner(client: TestClient, auth_headers):
    headers = auth_headers(_unique("owner"), role="owner")
    # Register a second user via signup so the list is non-trivial.
    client.post(
        "/api/v1/auth/signup",
        json={
            "tenant_id": "tenant-1",
            "email": _unique("member"),
            "password": "password123",
        },
    )
    response = client.get("/api/v1/admin/users", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_admin_change_role_allowed_for_owner(client: TestClient, auth_headers):
    headers = auth_headers(_unique("owner"), role="owner")
    target_email = _unique("target")
    signup = client.post(
        "/api/v1/auth/signup",
        json={
            "tenant_id": "tenant-1",
            "email": target_email,
            "password": "password123",
        },
    )
    target_id = signup.json()["id"]

    response = client.put(
        f"/api/v1/admin/users/{target_id}/role?new_role=manager",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["role"] == "manager"


def test_admin_change_role_forbidden_for_non_owner(client: TestClient, auth_headers):
    headers = auth_headers(_unique("manager"), role="manager")
    signup = client.post(
        "/api/v1/auth/signup",
        json={
            "tenant_id": "tenant-1",
            "email": _unique("target"),
            "password": "password123",
        },
    )
    target_id = signup.json()["id"]

    response = client.put(
        f"/api/v1/admin/users/{target_id}/role?new_role=manager",
        headers=headers,
    )
    assert response.status_code == 403


def test_admin_change_role_invalid_value(client: TestClient, auth_headers):
    headers = auth_headers(_unique("owner"), role="owner")
    signup = client.post(
        "/api/v1/auth/signup",
        json={
            "tenant_id": "tenant-1",
            "email": _unique("target"),
            "password": "password123",
        },
    )
    target_id = signup.json()["id"]

    response = client.put(
        f"/api/v1/admin/users/{target_id}/role?new_role=superuser",
        headers=headers,
    )
    assert response.status_code == 422  # Role enum rejects unknown values


def test_admin_deactivate_user_allowed_for_owner(client: TestClient, auth_headers):
    headers = auth_headers(_unique("owner"), role="owner")
    signup = client.post(
        "/api/v1/auth/signup",
        json={
            "tenant_id": "tenant-1",
            "email": _unique("target"),
            "password": "password123",
        },
    )
    target_id = signup.json()["id"]

    response = client.delete(f"/api/v1/admin/users/{target_id}", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"ok": True}

    # Verify user is now deactivated.
    response = client.get("/api/v1/admin/users", headers=headers)
    target = next(u for u in response.json() if u["id"] == target_id)
    assert target["is_active"] is False


def test_admin_cannot_change_own_role(client: TestClient, auth_headers):
    email = _unique("owner")
    headers = auth_headers(email, role="owner")
    users = client.get("/api/v1/admin/users", headers=headers).json()
    owner_id = next(user["id"] for user in users if user["email"] == email)

    response = client.put(
        f"/api/v1/admin/users/{owner_id}/role?new_role=manager",
        headers=headers,
    )
    assert response.status_code == 400
    assert "own role" in response.json()["detail"]


def test_admin_cannot_deactivate_self_or_leave_no_active_owner(client: TestClient, auth_headers):
    email = _unique("owner")
    headers = auth_headers(email, role="owner")
    users = client.get("/api/v1/admin/users", headers=headers).json()
    owner_id = next(user["id"] for user in users if user["email"] == email)

    response = client.delete(f"/api/v1/admin/users/{owner_id}", headers=headers)
    assert response.status_code == 400
    assert "own account" in response.json()["detail"]


def test_admin_can_deactivate_another_owner_when_one_remains(client: TestClient, auth_headers):
    headers = auth_headers(_unique("owner"), role="owner")
    signup = client.post(
        "/api/v1/auth/signup",
        json={
            "tenant_id": "tenant-1",
            "email": _unique("second-owner"),
            "password": "password123",
        },
    )
    target_id = signup.json()["id"]
    promote = client.put(
        f"/api/v1/admin/users/{target_id}/role?new_role=owner",
        headers=headers,
    )
    assert promote.status_code == 200

    response = client.delete(f"/api/v1/admin/users/{target_id}", headers=headers)
    assert response.status_code == 200


def test_services_cannot_remove_the_last_active_owner(db_session: Session):
    owner = User(
        id=str(uuid.uuid4()),
        tenant_id="tenant-1",
        email=_unique("owner"),
        hashed_password=get_password_hash("password123"),
        role="owner",
        is_active=True,
    )
    db_session.add(owner)
    db_session.commit()

    with pytest.raises(LastActiveOwnerError):
        update_user_role(db_session, user_id=owner.id, new_role="manager")
    with pytest.raises(LastActiveOwnerError):
        deactivate_user(db_session, user_id=owner.id)


# ---------------------------------------------------------------------------
# require_roles enforcement on existing routers
# ---------------------------------------------------------------------------


def test_client_cannot_create_project(client: TestClient, auth_headers):
    headers = auth_headers(_unique("client"), role="client")
    response = client.post(
        "/api/v1/projects/",
        json={"tenant_id": "tenant-1", "client_id": "c1", "name": "New"},
        headers=headers,
    )
    assert response.status_code == 403


def test_member_cannot_create_project(client: TestClient, auth_headers):
    """Member role is NOT allowed to create projects — only OWNER and MANAGER."""
    headers = auth_headers(_unique("member"), role="member")
    response = client.post(
        "/api/v1/projects/",
        json={"tenant_id": "tenant-1", "client_id": "c1", "name": "New"},
        headers=headers,
    )
    assert response.status_code == 403


def test_manager_can_create_project(client: TestClient, auth_headers, seed_tenant_client):
    headers = auth_headers(_unique("manager"), role="manager")
    response = client.post(
        "/api/v1/projects/",
        json={
            "tenant_id": seed_tenant_client["tenant_id"],
            "client_id": seed_tenant_client["client_id"],
            "name": "New",
        },
        headers=headers,
    )
    assert response.status_code in (200, 201)


def test_client_cannot_create_lead(client: TestClient, auth_headers):
    headers = auth_headers(_unique("client"), role="client")
    response = client.post(
        "/api/v1/leads/",
        json={
            "tenant_id": "tenant-1",
            "client_id": "c1",
            "raw_text": "Test lead body",
        },
        headers=headers,
    )
    assert response.status_code == 403


def test_member_can_create_lead(client: TestClient, auth_headers, seed_tenant_client):
    headers = auth_headers(_unique("member"), role="member")
    response = client.post(
        "/api/v1/leads/",
        json={
            "tenant_id": seed_tenant_client["tenant_id"],
            "client_id": seed_tenant_client["client_id"],
            "raw_text": "Test lead body",
        },
        headers=headers,
    )
    assert response.status_code in (200, 201)


def test_client_can_list_projects(client: TestClient, auth_headers):
    """Read endpoints should remain accessible to clients."""
    headers = auth_headers(_unique("client"), role="client")
    response = client.get("/api/v1/projects/tenant-1", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_unauthenticated_cannot_access_projects(client: TestClient):
    response = client.get("/api/v1/projects/tenant-1")
    assert response.status_code == 401
