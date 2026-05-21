import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    database_url: str
    jwt_secret: str
    jwt_algorithm: str
    access_token_minutes: int


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        database_url = os.getenv("DATABASE_URL", "")
        if not database_url:
            raise RuntimeError("DATABASE_URL is not set")
        _settings = Settings(
            database_url=database_url,
            jwt_secret=os.getenv("JWT_SECRET", "dev-secret-change-me"),
            jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
            access_token_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "20160")),
        )
    return _settings
