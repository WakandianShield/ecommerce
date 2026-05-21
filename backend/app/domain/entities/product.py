from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Product:
    id: str
    name: str
    description: Optional[str]
    price_cents: int
    stock: int
    category: Optional[str]
    image_url: Optional[str]
    is_active: bool


@dataclass(frozen=True)
class ProductCreate:
    name: str
    description: Optional[str]
    price_cents: int
    stock: int
    category: Optional[str]
    image_url: Optional[str]
    is_active: bool = True


@dataclass(frozen=True)
class ProductUpdate:
    name: Optional[str] = None
    description: Optional[str] = None
    price_cents: Optional[int] = None
    stock: Optional[int] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None
