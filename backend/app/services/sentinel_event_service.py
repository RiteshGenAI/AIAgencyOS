import uuid
from sqlalchemy.orm import Session

from backend.app.models.sentinel_event import SentinelEvent
from backend.app.schemas.sentinel_event_schema import SentinelEventRead
from backend.app.services.sentinel_service import SentinelScanResult


def record_sentinel_event(
    db: Session,
    tenant_id: str,
    entity_type: str,
    entity_id: str,
    scan_type: str,
    result: SentinelScanResult,
    project_id: str | None = None,
) -> SentinelEventRead:
    event = SentinelEvent(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        entity_type=entity_type,
        entity_id=entity_id,
        scan_type=scan_type,
        risk_score=result.risk_score,
        issues="\n".join(result.issues) if result.issues else None,
        project_id=project_id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return SentinelEventRead.model_validate(event)


def list_events_for_project(db: Session, project_id: str) -> list[SentinelEventRead]:
    q = db.query(SentinelEvent).filter(SentinelEvent.project_id == project_id)
    return [SentinelEventRead.model_validate(x) for x in q.all()]
