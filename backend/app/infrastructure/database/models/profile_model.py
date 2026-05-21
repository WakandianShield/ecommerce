from sqlalchemy import Column, DateTime, String
from sqlalchemy.sql import func

from app.infrastructure.database.connection import Base


class ProfileModel(Base):
    __tablename__ = "profiles"

    id = Column(String, primary_key=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
