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

    model_config = ConfigDict(from_attributes=True)
