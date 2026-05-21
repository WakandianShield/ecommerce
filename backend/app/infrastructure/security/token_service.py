from datetime import datetime, timedelta, timezone

from jose import jwt

from app.infrastructure.config.settings import get_settings


class TokenService:
    def __init__(self) -> None:
        self._settings = get_settings()

    def create_access_token(self, subject: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=self._settings.access_token_minutes)
        payload = {"sub": subject, "exp": expire}
        return jwt.encode(payload, self._settings.jwt_secret, algorithm=self._settings.jwt_algorithm)

    def decode_access_token(self, token: str) -> dict:
        return jwt.decode(token, self._settings.jwt_secret, algorithms=[self._settings.jwt_algorithm])
