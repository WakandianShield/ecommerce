from typing import Protocol, Optional

from app.domain.entities.profile import Profile, ProfileAuth


class ProfileRepository(Protocol):
    def get_by_id(self, profile_id: str) -> Optional[Profile]:
        ...

    def get_by_email(self, email: str) -> Optional[Profile]:
        ...

    def get_auth_by_email(self, email: str) -> Optional[ProfileAuth]:
        ...

    def create(self, full_name: str, email: str, password_hash: str, role: str) -> Profile:
        ...
