from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    tenant_id: str
    email: EmailStr
    role: str = "member"


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: str
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    tenant_id: str
    role: str
