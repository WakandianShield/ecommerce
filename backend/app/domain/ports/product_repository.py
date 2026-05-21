from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.product import Product


class ProductRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Product]: ...

    @abstractmethod
    def get_by_id(self, product_id: str) -> Optional[Product]: ...

    @abstractmethod
    def get_by_category(self, category: str) -> List[Product]: ...

    @abstractmethod
    def save(self, product: Product) -> Product: ...
