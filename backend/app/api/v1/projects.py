from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.core.config import Role
from backend.app.core.security import get_db, get_current_user, ensure_tenant, require_roles
from backend.app.models.project import Project
from backend.app.models.user import User
from backend.app.schemas.project_schema import ProjectCreate, ProjectRead
from backend.app.schemas.landing_page_schema import LandingPageRequestSchema
from backend.app.services.project_service import (
    create_project,
    update_project_scope,
    list_projects,
)
from backend.app.services.agent_service import call_landing_page_agent


router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectRead, dependencies=[Depends(require_roles(Role.OWNER, Role.MANAGER))])
async def create_project_endpoint(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectRead:
    ensure_tenant(current_user, project_in.tenant_id)
    try:
        return create_project(db, project_in)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/{tenant_id}",
    response_model=list[ProjectRead],
    dependencies=[Depends(require_roles(Role.OWNER, Role.MANAGER, Role.MEMBER, Role.CLIENT))],
)
async def list_projects_endpoint(
    tenant_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> list[ProjectRead]:
    ensure_tenant(current_user, tenant_id)
    return list_projects(db, tenant_id, skip=skip, limit=limit)


@router.post(
    "/{project_id}/scope",
    response_model=ProjectRead,
    dependencies=[Depends(require_roles(Role.OWNER, Role.MANAGER))],
)
async def scope_project_with_landing_workflow(
    project_id: str,
    request: LandingPageRequestSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectRead:
    project = db.query(Project).filter(Project.id == project_id, Project.tenant_id == request.tenant_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    ensure_tenant(current_user, request.tenant_id)

    lp_result = await call_landing_page_agent(request)
    summary = (
        f"Hero: {lp_result.draft.hero_headline}\n"
        f"Sections: {len(lp_result.draft.sections)}\n"
        f"Overall QA: {lp_result.qa.overall_score}"
    )

    return update_project_scope(db, project_id, scoped_summary=summary)
