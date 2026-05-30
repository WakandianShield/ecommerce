from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.infrastructure.config.settings import get_settings


Base = declarative_base()


def get_engine():
    settings = get_settings()
    return create_engine(settings.database_url, pool_pre_ping=True, future=True)


engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _ensure_chat_session_profile_id()


def _ensure_chat_session_profile_id() -> None:
    inspector = inspect(engine)
    if "chat_sessions" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("chat_sessions")}
    if "profile_id" in columns:
        return
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE chat_sessions ADD COLUMN profile_id VARCHAR(36)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_chat_sessions_profile_id ON chat_sessions (profile_id)"))
