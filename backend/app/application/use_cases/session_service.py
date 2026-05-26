from datetime import datetime, timezone
from typing import Protocol

from app.domain.entities.profile import Profile
from app.domain.errors import AuthError
from app.domain.ports.profile_repository import ProfileRepository
from app.domain.ports.refresh_token_repository import RefreshTokenRepository


class PasswordHasher(Protocol):
    def verify(self, password: str, password_hash: str) -> bool:
        ...


class TokenService(Protocol):
    def create_access_token(self, subject: str, role: str) -> str:
        ...

    def create_refresh_token(self, subject: str, role: str) -> tuple[str, str, datetime]:
        ...

    def decode_token(self, token: str) -> dict:
        ...


class SessionService:
    def __init__(
        self,
        repo: ProfileRepository,
        hasher: PasswordHasher,
        token_service: TokenService,
        refresh_repo: RefreshTokenRepository,
    ) -> None:
        self._repo = repo
        self._hasher = hasher
        self._token_service = token_service
        self._refresh_repo = refresh_repo

    def login(self, email: str, password: str):
        auth = self._repo.get_auth_by_email(email)
        if not auth:
            raise AuthError("Invalid credentials")
        if not self._hasher.verify(password, auth.password_hash):
            raise AuthError("Invalid credentials")
        access_token, refresh_token = self.issue_tokens(Profile(
            id=auth.id,
            full_name=auth.full_name,
            email=auth.email,
            role=auth.role,
        ))
        return access_token, refresh_token, auth

    def issue_tokens(self, profile: Profile) -> tuple[str, str]:
        access_token = self._token_service.create_access_token(profile.id, profile.role)
        refresh_token, token_id, expires_at = self._token_service.create_refresh_token(
            profile.id,
            profile.role,
        )
        self._refresh_repo.create(profile.id, token_id, expires_at)
        return access_token, refresh_token

    def refresh(self, refresh_token: str) -> tuple[str, str, Profile]:
        try:
            payload = self._token_service.decode_token(refresh_token)
        except Exception:
            raise AuthError("Invalid token")
        if payload.get("type") != "refresh":
            raise AuthError("Invalid token")
        token_id = payload.get("jti")
        profile_id = payload.get("sub")
        if not token_id or not profile_id:
            raise AuthError("Invalid token")
        stored = self._refresh_repo.get(token_id)
        if not stored or stored.revoked_at is not None:
            raise AuthError("Invalid token")
        if stored.profile_id != profile_id:
            raise AuthError("Invalid token")
        if stored.expires_at <= datetime.now(timezone.utc):
            raise AuthError("Token expired")
        profile = self._repo.get_by_id(profile_id)
        if not profile:
            raise AuthError("Profile not found")
        self._refresh_repo.revoke(token_id)
        access_token, new_refresh_token = self.issue_tokens(profile)
        return access_token, new_refresh_token, profile

    def logout(self, refresh_token: str) -> None:
        try:
            payload = self._token_service.decode_token(refresh_token)
        except Exception:
            raise AuthError("Invalid token")
        if payload.get("type") != "refresh":
            raise AuthError("Invalid token")
        token_id = payload.get("jti")
        if not token_id:
            raise AuthError("Invalid token")
        stored = self._refresh_repo.get(token_id)
        if not stored or stored.revoked_at is not None:
            raise AuthError("Invalid token")
        if stored.profile_id != payload.get("sub"):
            raise AuthError("Invalid token")
        self._refresh_repo.revoke(token_id)
