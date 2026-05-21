from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.profile import Profile


class ProfileRepository(ABC):
    @abstractmethod
    def get_by_id(self, profile_id: str) -> Optional[Profile]: ...

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[Profile]: ...

    @abstractmethod
    def save(self, profile: Profile) -> Profile: ...
