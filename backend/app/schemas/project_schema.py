from pydantic import BaseModel


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

    class Config:
        from_attributes = True
