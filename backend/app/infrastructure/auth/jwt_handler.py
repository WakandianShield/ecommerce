import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = os.getenv("JWT_SECRET", "change-this-in-production-please")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 14

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordHasher:
    def hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)


def create_access_token(profile_id: str, email: str) -> str:
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    payload = {"sub": profile_id, "email": email, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
