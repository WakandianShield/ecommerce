from dataclasses import dataclass


@dataclass(frozen=True)
class Profile:
    id: str
    full_name: str
    email: str


@dataclass(frozen=True)
class ProfileAuth:
    id: str
    full_name: str
    email: str
    password_hash: str
