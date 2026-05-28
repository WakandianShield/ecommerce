from typing import Protocol, List, Optional

from app.domain.entities.product import Product, ProductCreate, ProductUpdate


class ProductRepository(Protocol):
    def list(self) -> List[Product]:
        ...

    def get(self, product_id: str) -> Optional[Product]:
        ...

    def create(self, data: ProductCreate) -> Product:
        ...

    def update(self, product_id: str, data: ProductUpdate) -> Optional[Product]:
        ...

    def decrement_stock(self, product_quantities: dict[str, int]) -> None:
        ...

    def delete(self, product_id: str) -> bool:
        ...
