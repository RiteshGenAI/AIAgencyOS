from typing import Optional
from pydantic import BaseModel


class ProjectBase(BaseModel):
    tenant_id: str
    client_id: str
    name: str


class ProjectCreate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    id: str
    status: str
    scoped_summary: Optional[str] = None

    class Config:
        from_attributes = True
