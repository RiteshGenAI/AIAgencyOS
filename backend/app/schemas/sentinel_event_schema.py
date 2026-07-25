from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SentinelEventRead(BaseModel):
    id: str
    tenant_id: str
    entity_type: str
    entity_id: str
    scan_type: str
    risk_score: float
    issues: Optional[str] = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
