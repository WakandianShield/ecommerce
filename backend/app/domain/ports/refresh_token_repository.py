from datetime import datetime
from typing import Optional, Protocol

from app.domain.entities.refresh_token import RefreshToken


class RefreshTokenRepository(Protocol):
    def create(self, profile_id: str, token_id: str, expires_at: datetime) -> RefreshToken:
        ...

    def get(self, token_id: str) -> Optional[RefreshToken]:
        ...

    def revoke(self, token_id: str) -> bool:
        ...
