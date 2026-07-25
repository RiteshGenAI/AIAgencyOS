from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class LeadBase(BaseModel):
    tenant_id: str
    client_id: Optional[str] = None
    source: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    raw_text: str


class LeadCreate(LeadBase):
    pass


class LeadRead(LeadBase):
    id: str
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
