from datetime import datetime, timedelta, timezone
import uuid

from jose import jwt

from app.infrastructure.config.settings import get_settings


class TokenService:
    def __init__(self) -> None:
        self._settings = get_settings()

    def create_access_token(self, subject: str, role: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=self._settings.access_token_minutes)
        payload = {"sub": subject, "role": role, "type": "access", "exp": expire}
        return jwt.encode(payload, self._settings.jwt_secret, algorithm=self._settings.jwt_algorithm)

    def create_refresh_token(self, subject: str, role: str) -> tuple[str, str, datetime]:
        expire = datetime.now(timezone.utc) + timedelta(days=self._settings.refresh_token_days)
        token_id = str(uuid.uuid4())
        payload = {"sub": subject, "role": role, "type": "refresh", "jti": token_id, "exp": expire}
        token = jwt.encode(payload, self._settings.jwt_secret, algorithm=self._settings.jwt_algorithm)
        return token, token_id, expire

    def decode_token(self, token: str) -> dict:
        return jwt.decode(token, self._settings.jwt_secret, algorithms=[self._settings.jwt_algorithm])
