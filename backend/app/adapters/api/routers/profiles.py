from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.adapters.api.dependencies import get_current_profile, get_db
from app.adapters.api.schemas import ProfileCreateIn, ProfileOut, SessionOut
from app.application.use_cases.session_service import SessionService
from app.application.use_cases.profile_service import ProfileService
from app.domain.errors import ValidationError
from app.infrastructure.database.repositories import (
    SqlAlchemyProfileRepository,
    SqlAlchemyRefreshTokenRepository,
)
from app.infrastructure.security.password_hasher import PasswordHasher
from app.infrastructure.security.token_service import TokenService


router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def register_profile(payload: ProfileCreateIn, db: Session = Depends(get_db)):
    service = ProfileService(SqlAlchemyProfileRepository(db), PasswordHasher())
    try:
        profile = service.register(payload.full_name, payload.email, payload.password)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    session_service = SessionService(
        SqlAlchemyProfileRepository(db),
        PasswordHasher(),
        TokenService(),
        SqlAlchemyRefreshTokenRepository(db),
    )
    access_token, refresh_token = session_service.issue_tokens(profile)
    return SessionOut(
        access_token=access_token,
        refresh_token=refresh_token,
        profile=ProfileOut.model_validate(profile),
    )


@router.get("/me", response_model=ProfileOut)
def get_me(profile=Depends(get_current_profile)):
    return ProfileOut.model_validate(profile)
