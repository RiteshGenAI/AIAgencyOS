from typing import Optional
from pydantic import BaseModel


class SentinelEventRead(BaseModel):
    id: str
    tenant_id: str
    entity_type: str
    entity_id: str
    scan_type: str
    risk_score: float
    issues: Optional[str] = None

    class Config:
        from_attributes = True
