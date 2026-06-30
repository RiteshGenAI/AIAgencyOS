from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.config import Role
from backend.app.core.security import get_db, get_current_user, ensure_tenant, require_roles
from backend.app.models.project import Project
from backend.app.models.user import User
from backend.app.schemas.landing_page_schema import (
    LandingPageRequestSchema,
    ProductionLandingPageSchema,
)
from backend.app.services.agent_service import call_landing_page_agent
from backend.app.services.sentinel_service import (
    sentinel_scan,
    SentinelScanInput,
)


router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post(
    "/{project_id}/landing-page",
    response_model=ProductionLandingPageSchema,
    dependencies=[Depends(require_roles(Role.OWNER, Role.MANAGER, Role.MEMBER))],
)
async def generate_landing_page_copy(
    project_id: str,
    req: LandingPageRequestSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProductionLandingPageSchema:
    project = db.query(Project).filter(Project.id == project_id, Project.tenant_id == req.tenant_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    ensure_tenant(current_user, req.tenant_id)
    # optional quick Sentinel scan at API boundary
    scan_result = await sentinel_scan(
        SentinelScanInput(
            payload=req.brief_text,
            policy_id=req.policy_id,
            scan_type="prompt",
        )
    )
    if not scan_result.allowed:
        raise HTTPException(status_code=400, detail="Brief blocked by Sentinel")

    result = await call_landing_page_agent(req)
    # TODO: persist result to DB and S3
    return result
