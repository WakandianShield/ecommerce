from typing import Protocol

from app.domain.entities.profile import Profile
from app.domain.errors import ValidationError
from app.domain.ports.profile_repository import ProfileRepository


class PasswordHasher(Protocol):
    def hash(self, password: str) -> str:
        ...


class ProfileService:
    def __init__(self, repo: ProfileRepository, hasher: PasswordHasher) -> None:
        self._repo = repo
        self._hasher = hasher

    def register(self, full_name: str, email: str, password: str) -> Profile:
        if not full_name.strip():
            raise ValidationError("Full name is required")
        if not email.strip():
            raise ValidationError("Email is required")
        if not password:
            raise ValidationError("Password is required")
        existing = self._repo.get_by_email(email)
        if existing:
            raise ValidationError("Email is already registered")
        password_hash = self._hasher.hash(password)
        return self._repo.create(full_name=full_name, email=email, password_hash=password_hash)
