from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.infrastructure.database.connection import Base


class OrderItemModel(Base):
    __tablename__ = "order_items"

    id = Column(String, primary_key=True)
    order_id = Column(String, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price_cents = Column(Integer, nullable=False)
    image_url = Column(String, nullable=False, default="")


class OrderModel(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True)
    profile_id = Column(String, ForeignKey("profiles.id"), nullable=False, index=True)
    status = Column(String, nullable=False, default="confirmed")
    shipping_address = Column(String, nullable=False)
    total_cents = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    items = relationship("OrderItemModel", cascade="all, delete-orphan", lazy="joined")
