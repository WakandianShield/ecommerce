from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities.profile import Profile
from app.domain.ports.profile_repository import ProfileRepository
from app.infrastructure.database.models.profile_model import ProfileModel


class PgProfileRepository(ProfileRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, profile_id: str) -> Optional[Profile]:
        model = self.session.query(ProfileModel).filter_by(id=profile_id).first()
        return self._to_entity(model) if model else None

    def get_by_email(self, email: str) -> Optional[Profile]:
        model = self.session.query(ProfileModel).filter_by(email=email).first()
        return self._to_entity(model) if model else None

    def save(self, profile: Profile) -> Profile:
        model = self.session.query(ProfileModel).filter_by(id=profile.id).first()
        if model:
            model.full_name = profile.full_name
            model.email = profile.email
            model.password_hash = profile.password_hash
        else:
            model = ProfileModel(
                id=profile.id,
                full_name=profile.full_name,
                email=profile.email,
                password_hash=profile.password_hash,
            )
            self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: ProfileModel) -> Profile:
        return Profile(
            id=model.id,
            full_name=model.full_name,
            email=model.email,
            password_hash=model.password_hash,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
