import strawberry

from app.domain.entities.profile import Profile


@strawberry.type
class UserProfileType:
    id: strawberry.ID
    full_name: str
    email: str

    @classmethod
    def from_entity(cls, profile: Profile) -> "UserProfileType":
        return cls(id=profile.id, full_name=profile.full_name, email=profile.email)


@strawberry.type
class AuthPayloadType:
    token: str
    user: UserProfileType
