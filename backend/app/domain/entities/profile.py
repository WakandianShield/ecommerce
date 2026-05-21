from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Profile:
    id: str
    full_name: str
    email: str
    password_hash: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
