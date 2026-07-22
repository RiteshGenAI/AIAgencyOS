from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.security import get_db
from backend.app.schemas.user_schema import LoginRequest, SignupRequest, UserRead, Token
from backend.app.services.auth_service import (
    create_user,
    authenticate_user,
    create_access_token,
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
