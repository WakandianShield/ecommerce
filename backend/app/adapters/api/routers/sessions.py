from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.adapters.api.dependencies import get_db
from app.adapters.api.schemas import ProfileOut, RefreshTokenIn, SessionIn, SessionOut
from app.application.use_cases.session_service import SessionService
from app.domain.entities.profile import Profile
from app.domain.errors import AuthError
from app.infrastructure.database.repositories import (
    SqlAlchemyProfileRepository,
    SqlAlchemyRefreshTokenRepository,
)
from app.infrastructure.security.password_hasher import PasswordHasher
from app.infrastructure.security.token_service import TokenService


router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionOut)
def create_session(payload: SessionIn, db: Session = Depends(get_db)):
    service = SessionService(
        SqlAlchemyProfileRepository(db),
        PasswordHasher(),
        TokenService(),
        SqlAlchemyRefreshTokenRepository(db),
    )
    try:
        access_token, refresh_token, auth = service.login(payload.email, payload.password)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    profile = Profile(id=auth.id, full_name=auth.full_name, email=auth.email, role=auth.role)
    return SessionOut(
        access_token=access_token,
        refresh_token=refresh_token,
        profile=ProfileOut.model_validate(profile),
    )


@router.post("/refresh", response_model=SessionOut)
def refresh_session(payload: RefreshTokenIn, db: Session = Depends(get_db)):
    service = SessionService(
        SqlAlchemyProfileRepository(db),
        PasswordHasher(),
        TokenService(),
        SqlAlchemyRefreshTokenRepository(db),
    )
    try:
        access_token, refresh_token, profile = service.refresh(payload.refresh_token)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    return SessionOut(
        access_token=access_token,
        refresh_token=refresh_token,
        profile=ProfileOut.model_validate(profile),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: RefreshTokenIn, db: Session = Depends(get_db)):
    service = SessionService(
        SqlAlchemyProfileRepository(db),
        PasswordHasher(),
        TokenService(),
        SqlAlchemyRefreshTokenRepository(db),
    )
    try:
        service.logout(payload.refresh_token)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    return None
