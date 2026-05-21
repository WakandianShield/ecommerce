from app.domain.entities.profile import Profile
from app.domain.exceptions import ProfileNotFound
from app.domain.ports.profile_repository import ProfileRepository


class GetProfile:
    def __init__(self, repo: ProfileRepository):
        self.repo = repo

    def execute(self, profile_id: str) -> Profile:
        profile = self.repo.get_by_id(profile_id)
        if not profile:
            raise ProfileNotFound(f"Profile {profile_id} not found")
        return profile
