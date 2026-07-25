from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class ClientBase(BaseModel):
    tenant_id: str
    name: str
    contact_email: EmailStr | None = None


class ClientCreate(ClientBase):
    reference_id: str | None = None


class ClientRead(ClientBase):
    id: str
    reference_id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
