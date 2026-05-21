from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class OrderItem:
    id: str
    product_id: Optional[str]
    name: str
    unit_price_cents: int
    quantity: int


@dataclass(frozen=True)
class Order:
    id: str
    profile_id: str
    status: str
    total_cents: int
    shipping_address: str
    items: List[OrderItem]


@dataclass(frozen=True)
class OrderItemCreate:
    product_id: Optional[str]
    name: str
    unit_price_cents: int
    quantity: int


@dataclass(frozen=True)
class OrderCreate:
    profile_id: str
    shipping_address: str
    items: List[OrderItemCreate]
