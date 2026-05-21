from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class OrderItem:
    id: str
    order_id: str
    product_name: str
    quantity: int
    unit_price_cents: int
    image_url: str


@dataclass
class Order:
    id: str
    profile_id: str
    status: str
    shipping_address: str
    total_cents: int
    items: List[OrderItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
