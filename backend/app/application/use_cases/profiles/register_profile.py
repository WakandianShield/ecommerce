import uuid

from app.domain.entities.profile import Profile
from app.domain.exceptions import ProfileAlreadyExists
from app.domain.ports.profile_repository import ProfileRepository


class RegisterProfile:
    def __init__(self, repo: ProfileRepository, hasher):
        self.repo = repo
        self.hasher = hasher

    def execute(self, full_name: str, email: str, password: str) -> Profile:
        if self.repo.get_by_email(email):
            raise ProfileAlreadyExists(f"Email {email} is already registered")

        profile = Profile(
            id=str(uuid.uuid4()),
            full_name=full_name,
            email=email,
            password_hash=self.hasher.hash(password),
        )
        return self.repo.save(profile)
