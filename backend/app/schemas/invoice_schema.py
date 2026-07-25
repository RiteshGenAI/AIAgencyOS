from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InvoiceBase(BaseModel):
    tenant_id: str
    project_id: str
    amount: float
    currency: str = "USD"


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceRead(InvoiceBase):
    id: str
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
