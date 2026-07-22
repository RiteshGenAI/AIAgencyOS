import uuid
from sqlalchemy.orm import Session

from backend.app.models.client import Client
from backend.app.models.project import Project
from backend.app.models.tenant import Tenant
from backend.app.schemas.project_schema import ProjectCreate, ProjectRead


def create_project(db: Session, project_in: ProjectCreate) -> ProjectRead:
    if not db.query(Tenant).filter(Tenant.id == project_in.tenant_id).first():
        raise ValueError("Tenant not found")
    if not db.query(Client).filter(Client.id == project_in.client_id).first():
        raise ValueError("Client not found")
    project = Project(
        id=str(uuid.uuid4()),
        tenant_id=project_in.tenant_id,
        client_id=project_in.client_id,
        name=project_in.name,
        status="draft",
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return ProjectRead.model_validate(project)


def update_project_scope(
    db: Session, project_id: str, scoped_summary: str, status: str = "scoped"
) -> ProjectRead:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ValueError("Project not found")
    project.scoped_summary = scoped_summary
    project.status = status
    db.commit()
    db.refresh(project)
    return ProjectRead.model_validate(project)


def list_projects(db: Session, tenant_id: str) -> list[ProjectRead]:
    q = db.query(Project).filter(Project.tenant_id == tenant_id)
    return [ProjectRead.model_validate(x) for x in q.all()]
