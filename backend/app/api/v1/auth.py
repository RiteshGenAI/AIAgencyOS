from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.security import get_db, get_current_user
from backend.app.schemas.user_schema import (
    EmailVerifyRequest,
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    SignupRequest,
    UserRead,
    Token,
)
from backend.app.services.auth_service import (
    create_user,
    authenticate_user,
    create_access_token,
    confirm_password_reset,
    request_password_reset,
    verify_email,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserRead)
async def signup(user_in: SignupRequest, db: Session = Depends(get_db)) -> UserRead:
    return create_user(db, user_in)


@router.post("/login", response_model=Token)
async def login(body: LoginRequest, db: Session = Depends(get_db)) -> Token:
    """Authenticate with a JSON body (``{"email": "...", "password": "..."}``).

    Returns a JWT access token on success, or 401 on invalid credentials.
    """
    user = authenticate_user(db, email=body.email, password=body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return create_access_token(
        user=user,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


@router.post("/forgot-password")
async def forgot_password(body: PasswordResetRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    request_password_reset(db, body.email)
    return {"message": "If an account exists, a reset link has been sent."}


@router.post("/reset-password")
async def reset_password(body: PasswordResetConfirm, db: Session = Depends(get_db)) -> dict[str, str]:
    confirm_password_reset(db, body.token, body.new_password)
    return {"message": "Password reset successful"}


@router.post("/verify-email")
async def verify_email_endpoint(body: EmailVerifyRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    verify_email(db, body.token)
    return {"message": "Email verified successfully"}


@router.get("/verification-status")
async def verification_status(current_user = Depends(get_current_user)) -> dict[str, bool]:
    return {"is_verified": current_user.is_verified}
