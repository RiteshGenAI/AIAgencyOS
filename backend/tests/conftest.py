"""Test configuration: ensures tests run against a dedicated PostgreSQL database.

All tests MUST use PostgreSQL — no SQLite or any other database is allowed.
The test database (``agency_os_test`` by default) is created on demand if it
does not already exist, and its schema is rebuilt before each test so that
tests are fully isolated.

Required services:
    A PostgreSQL instance reachable via ``TEST_DATABASE_URL`` (default
    ``postgresql+psycopg2://postgres:postgres@localhost:5432/agency_os_test``).
    The simplest way to provide one locally is::

        docker compose up -d db

Override the URL via the ``TEST_DATABASE_URL`` environment variable, e.g.::

    TEST_DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/my_test_db pytest
"""

from __future__ import annotations

import os
import sys
import urllib.parse as _urlparse
import uuid
from typing import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


# ---------------------------------------------------------------------------
# Path setup — add backend/ and workspace root so `from backend.app...` works.
# ---------------------------------------------------------------------------
_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.dirname(_TESTS_DIR)
_WORKSPACE_ROOT = os.path.dirname(_BACKEND_DIR)
for _p in (_BACKEND_DIR, _WORKSPACE_ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)


# ---------------------------------------------------------------------------
# Required environment for the app to load safely under tests.
# ---------------------------------------------------------------------------
os.environ.setdefault("BACKEND_SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault(
    "BACKEND_DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/agency_os",
)
# Point the app's settings at the test database so any internal code that
# resolves `settings.DATABASE_URL` (e.g. migrations, init scripts) hits the
# test DB instead of the dev DB.
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://agency_os:agency_os@db:5432/agency_os_test",
)
os.environ["BACKEND_DATABASE_URL"] = TEST_DATABASE_URL


# ---------------------------------------------------------------------------
# Database bootstrap — ensure the test database exists, then connect.
# ---------------------------------------------------------------------------
def _split_admin_and_db(url: str) -> tuple[str, str]:
    """Return (admin_url, db_name) for CREATE DATABASE if needed."""
    parsed = _urlparse.urlparse(url)
    db_name = parsed.path.lstrip("/")
    admin_path = "/postgres"
    admin_url = _urlparse.urlunparse(parsed._replace(path=admin_path))
    return admin_url, db_name


def _ensure_test_database_exists(url: str) -> None:
    parsed = _urlparse.urlparse(url)
    if not parsed.scheme.startswith("postgres"):
        raise RuntimeError(
            f"TEST_DATABASE_URL must be a PostgreSQL URL, got: {url!r}. "
            "SQLite and other databases are not allowed for tests."
        )
    db_name = parsed.path.lstrip("/")
    if not db_name:
        raise RuntimeError(f"TEST_DATABASE_URL is missing a database name: {url!r}")

    admin_url, _ = _split_admin_and_db(url)
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        with admin_engine.connect() as conn:
            exists = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :n"),
                {"n": db_name},
            ).scalar()
            if not exists:
                # Identifiers cannot be parameterised; sanitise the name.
                safe = db_name.replace('"', '""')
                conn.execute(text(f'CREATE DATABASE "{safe}"'))
    finally:
        admin_engine.dispose()


_ensure_test_database_exists(TEST_DATABASE_URL)

engine: Engine = create_engine(TEST_DATABASE_URL, future=True, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


# ---------------------------------------------------------------------------
# Wire the FastAPI app to use the test database.
# ---------------------------------------------------------------------------
from backend.app.main import app  # noqa: E402 — must come after env setup
from backend.app.db.session import Base, get_db  # noqa: E402


def _override_get_db() -> Iterator[Session]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


# ---------------------------------------------------------------------------
# Disable middleware that interferes with tests.
# - RateLimitingMiddleware would block login/signup after 15 requests/min/IP,
#   which breaks the test suite.
# ---------------------------------------------------------------------------
app.user_middleware = [
    m for m in app.user_middleware if m.cls.__name__ != "RateLimitingMiddleware"
]
app.middleware_stack = app.build_middleware_stack()


# ---------------------------------------------------------------------------
# Fixtures.
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def _create_schema_once() -> Iterator[None]:
    """Create all tables once per test session."""
    Base.metadata.create_all(bind=engine)
    yield
    # Leave the schema in place after the run; the per-test truncate handles isolation.


@pytest.fixture(autouse=True)
def _truncate_tables() -> Iterator[None]:
    """Wipe every table before each test so tests are fully isolated."""
    table_names = ", ".join(
        f'"{t.name}"' for t in reversed(Base.metadata.sorted_tables)
    )
    with engine.begin() as conn:
        if table_names:
            conn.execute(text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE"))
    yield


@pytest.fixture
def client() -> TestClient:
    """A fresh TestClient with no auth header set."""
    return TestClient(app)


@pytest.fixture
def db_session() -> Iterator[Session]:
    """Provide a database session for service-level invariant tests."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def auth_headers():
    """Create a privileged test user directly and return auth headers.

    Usage::

        def test_foo(auth_headers):
            headers = auth_headers(email="...", role="manager")
            response = client.get("/api/v1/admin/users", headers=headers)
    """

    def _make(email: str, role: str, password: str = "password123", tenant_id: str = "tenant-1") -> dict[str, str]:
        from backend.app.models.user import User
        from backend.app.services.auth_service import create_access_token, get_password_hash

        db = TestingSessionLocal()
        try:
            user = User(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                email=email.lower(),
                hashed_password=get_password_hash(password),
                role=role,
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            token = create_access_token(user=user).access_token
            return {"Authorization": f"Bearer {token}"}
        finally:
            db.close()

    return _make


@pytest.fixture
def seed_tenant_client():
    """Insert a default Tenant and Client so project/lead FK constraints pass.

    Returns a dict ``{"tenant_id": ..., "client_id": ...}``. Use this fixture
    in any test that creates a Project or Lead, since both have FK constraints
    to ``tenants`` and ``clients``.
    """
    from backend.app.models.client import Client
    from backend.app.models.tenant import Tenant

    db = TestingSessionLocal()
    try:
        tenant = Tenant(id="tenant-1", name="Test Tenant")
        client_row = Client(
            id="client-1",
            tenant_id="tenant-1",
            name="Test Client",
            contact_email="client-1@example.com",
            reference_id="CID-0001",
        )
        db.merge(tenant)
        db.merge(client_row)
        db.commit()
    finally:
        db.close()
    return {"tenant_id": "tenant-1", "client_id": "client-1"}
