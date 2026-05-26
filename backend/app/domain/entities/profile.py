from dataclasses import dataclass


ROLE_CUSTOMER = "customer"
ROLE_ADMIN = "admin"
ROLE_OPERATOR = "operator"
ALLOWED_ROLES = {ROLE_CUSTOMER, ROLE_ADMIN, ROLE_OPERATOR}


@dataclass(frozen=True)
class Profile:
    id: str
    full_name: str
    email: str
    role: str


@dataclass(frozen=True)
class ProfileAuth:
    id: str
    full_name: str
    email: str
    role: str
    password_hash: str
