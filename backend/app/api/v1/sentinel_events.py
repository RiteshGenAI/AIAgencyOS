from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.security import get_db, get_current_user, ensure_tenant
from backend.app.models.user import User
from backend.app.schemas.sentinel_event_schema import SentinelEventRead
from backend.app.services.sentinel_event_service import list_events_for_project
from backend.app.models.project import Project


router = APIRouter(prefix="/sentinel-events", tags=["sentinel"])


@router.get("/project/{project_id}", response_model=list[SentinelEventRead])
async def get_project_events(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SentinelEventRead]:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return []
    ensure_tenant(current_user, project.tenant_id)
    return list_events_for_project(db, project_id)
