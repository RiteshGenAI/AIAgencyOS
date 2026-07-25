from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProjectBase(BaseModel):
    tenant_id: str
    client_id: str
    name: str
    description: str | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    id: str
    status: str
    scoped_summary: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
