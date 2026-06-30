import uuid

from backend.app.db.session import SessionLocal
from backend.app.models.tenant import Tenant
from backend.app.models.client import Client
from backend.app.models.project import Project
from backend.app.models.user import User
from backend.app.services.auth_service import get_password_hash


DEMO_TENANT_ID = "demo-tenant"
DEMO_CLIENT_ID = "demo-client"
DEMO_PROJECT_ID = "demo-project"
DEMO_USER_EMAIL = "admin@agency.local"
DEMO_USER_PASSWORD = "admin1234"


def seed() -> None:
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter(Tenant.id == DEMO_TENANT_ID).first()
        if not tenant:
            tenant = Tenant(id=DEMO_TENANT_ID, name="Demo Agency")
            db.add(tenant)
            db.commit()
            print(f"Seeded tenant: {DEMO_TENANT_ID}")

        client = db.query(Client).filter(Client.id == DEMO_CLIENT_ID).first()
        if not client:
            client = Client(
                id=DEMO_CLIENT_ID,
                tenant_id=DEMO_TENANT_ID,
                name="Demo Client",
                contact_email="client@example.com",
            )
            db.add(client)
            db.commit()
            print(f"Seeded client: {DEMO_CLIENT_ID}")

        project = db.query(Project).filter(Project.id == DEMO_PROJECT_ID).first()
        if not project:
            project = Project(
                id=DEMO_PROJECT_ID,
                tenant_id=DEMO_TENANT_ID,
                client_id=DEMO_CLIENT_ID,
                name="Landing Page Refresh",
                status="active",
                scoped_summary="Demo project for local development.",
            )
            db.add(project)
            db.commit()
            print(f"Seeded project: {DEMO_PROJECT_ID}")

        user = db.query(User).filter(User.email == DEMO_USER_EMAIL).first()
        if not user:
            user = User(
                id=str(uuid.uuid4()),
                tenant_id=DEMO_TENANT_ID,
                email=DEMO_USER_EMAIL,
                hashed_password=get_password_hash(DEMO_USER_PASSWORD),
                role="owner",
            )
            db.add(user)
            db.commit()
            print(f"Seeded user: {DEMO_USER_EMAIL} / {DEMO_USER_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
