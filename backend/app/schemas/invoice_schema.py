from pydantic import BaseModel


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

    class Config:
        from_attributes = True
