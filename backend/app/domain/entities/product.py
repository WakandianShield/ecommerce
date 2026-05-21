from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Product:
    id: str
    name: str
    artist: str
    year: int
    price_cents: int
    category: str
    image_url: str
    stock: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
