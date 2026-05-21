from typing import Protocol

from app.domain.errors import AuthError
from app.domain.ports.profile_repository import ProfileRepository


class PasswordHasher(Protocol):
    def verify(self, password: str, password_hash: str) -> bool:
        ...


class TokenService(Protocol):
    def create_access_token(self, subject: str) -> str:
        ...


class SessionService:
    def __init__(self, repo: ProfileRepository, hasher: PasswordHasher, token_service: TokenService) -> None:
        self._repo = repo
        self._hasher = hasher
        self._token_service = token_service

    def login(self, email: str, password: str):
        auth = self._repo.get_auth_by_email(email)
        if not auth:
            raise AuthError("Invalid credentials")
        if not self._hasher.verify(password, auth.password_hash):
            raise AuthError("Invalid credentials")
        token = self._token_service.create_access_token(auth.id)
        return token, auth
