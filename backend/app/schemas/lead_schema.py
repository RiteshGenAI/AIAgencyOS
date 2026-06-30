from typing import Optional
from pydantic import BaseModel


class LeadBase(BaseModel):
    tenant_id: str
    client_id: Optional[str] = None
    source: Optional[str] = None
    raw_text: str


class LeadCreate(LeadBase):
    pass


class LeadRead(LeadBase):
    id: str
    status: str

    class Config:
        from_attributes = True
