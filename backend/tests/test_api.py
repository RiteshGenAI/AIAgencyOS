import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.main import app
from backend.app.db.session import Base, get_db

TEST_DB_URL = "sqlite:///./test_shared.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    from sqlalchemy.orm import close_all_sessions

    close_all_sessions()
    with engine.begin() as conn:
        for tbl in reversed(Base.metadata.sorted_tables):
            conn.execute(tbl.delete())


@pytest.fixture
def authenticated_client():
    client.post(
        "/api/v1/auth/signup",
        json={
            "tenant_id": "tenant-1",
            "email": "auth@example.com",
            "password": "password123",
            "role": "member",
        },
    )
    login = client.post(
        "/api/v1/auth/login",
        data={"username": "auth@example.com", "password": "password123"},
    )
    token = login.json()["access_token"]
    authed = TestClient(app)
    authed.headers.update({"Authorization": f"Bearer {token}"})
    return authed


def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_db():
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    assert response.json()["database"] == "ok"


def test_signup_and_login():
    signup = client.post(
        "/api/v1/auth/signup",
        json={
            "tenant_id": "tenant-1",
            "email": "test@example.com",
            "password": "password123",
            "role": "member",
        },
    )
    assert signup.status_code == 200
    assert signup.json()["email"] == "test@example.com"

    login = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "password123"},
    )
    assert login.status_code == 200
    assert "access_token" in login.json()


def test_login_invalid():
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "nope@example.com", "password": "wrong"},
    )
    assert response.status_code == 401


def test_signup_duplicate_email():
    client.post(
        "/api/v1/auth/signup",
        json={"tenant_id": "tenant-1", "email": "dup@example.com", "password": "password123", "role": "member"},
    )
    response = client.post(
        "/api/v1/auth/signup",
        json={"tenant_id": "tenant-1", "email": "dup@example.com", "password": "password123", "role": "member"},
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_projects_require_auth():
    response = client.get("/api/v1/projects/demo-tenant")
    assert response.status_code == 401


def test_create_invoice_missing_project():
    # signup + login inline
    client.post(
        "/api/v1/auth/signup",
        json={"tenant_id": "tenant-1", "email": "inv@example.com", "password": "password123", "role": "member"},
    )
    login = client.post("/api/v1/auth/login", data={"username": "inv@example.com", "password": "password123"})
    token = login.json()["access_token"]
    resp = client.post(
        "/api/v1/invoices/",
        json={"tenant_id": "tenant-1", "project_id": "nonexistent", "amount": 100.0, "currency": "USD"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


def test_internal_sentinel_scan():
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
