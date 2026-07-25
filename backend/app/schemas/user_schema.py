from datetime import datetime

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from backend.app.core.config import Role


class UserBase(BaseModel):
    tenant_id: str
    email: EmailStr
    role: str = "member"


class SignupRequest(BaseModel):
    """Public registration payload."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    tenant_id: str
    email: EmailStr
    password: str = Field(min_length=8)
    role: Role = Role.MEMBER

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, v: object) -> Role:
        if isinstance(v, Role):
            return v
        if isinstance(v, str):
            try:
                return Role(v.strip().lower())
            except ValueError:
                raise ValueError(f"role must be one of {sorted(Role.values())}")
        raise ValueError("role must be a string")

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        has_letter = any(c.isalpha() for c in v)
        has_digit = any(c.isdigit() for c in v)
        if not has_letter or not has_digit:
            raise ValueError("Password must contain at least one letter and one number")
        return v


class LoginRequest(BaseModel):
    """JSON body for the login endpoint.

    Uses ``email`` and ``password`` fields (rather than the OAuth2 form-encoded
    ``username``/``password`` pair) so frontends can authenticate with a
    straightforward POST + JSON body.
    """

    email: EmailStr
    password: str = Field(min_length=1)


class UserRead(BaseModel):
    """Public user identity returned by admin endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    email: str
    role: str
    is_active: bool
    is_verified: bool = False
    created_at: datetime | None = None


class UserSession(BaseModel):
    """Identity returned alongside an access token for frontend session state."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    email: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserSession


class TokenPayload(BaseModel):
    sub: str
    tenant_id: str
    role: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        has_letter = any(c.isalpha() for c in v)
        has_digit = any(c.isdigit() for c in v)
        if not has_letter or not has_digit:
            raise ValueError("Password must contain at least one letter and one number")
        return v


class EmailVerifyRequest(BaseModel):
    token: str


class PasswordResetTokenRead(BaseModel):
    id: str
    user_id: str
    expires_at: datetime | None = None
    used: bool = False

    model_config = ConfigDict(from_attributes=True)
