from sqlalchemy import create_engine
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
