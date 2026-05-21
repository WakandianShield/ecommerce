from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.infrastructure.database.connection import Base


class ProductModel(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    price_cents = Column(Integer, nullable=False)
    category = Column(String, nullable=False, index=True)
    image_url = Column(String, nullable=False, default="")
    stock = Column(Integer, nullable=False, default=100)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
