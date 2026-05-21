from app.domain.entities.profile import Profile
from app.domain.exceptions import InvalidCredentials, ProfileNotFound
from app.domain.ports.profile_repository import ProfileRepository


class LoginProfile:
    def __init__(self, repo: ProfileRepository, hasher):
        self.repo = repo
        self.hasher = hasher

    def execute(self, email: str, password: str) -> Profile:
        profile = self.repo.get_by_email(email)
        if not profile:
            raise InvalidCredentials("Invalid email or password")

        if not self.hasher.verify(password, profile.password_hash):
            raise InvalidCredentials("Invalid email or password")

        return profile
