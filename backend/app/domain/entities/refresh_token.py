from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class RefreshToken:
    id: str
    profile_id: str
    expires_at: datetime
    revoked_at: Optional[datetime]
