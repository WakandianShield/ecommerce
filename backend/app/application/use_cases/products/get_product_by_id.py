from typing import Optional

from app.domain.entities.product import Product
from app.domain.exceptions import ProductNotFound
from app.domain.ports.product_repository import ProductRepository


class GetProductById:
    def __init__(self, repo: ProductRepository):
        self.repo = repo

    def execute(self, product_id: str) -> Product:
        product = self.repo.get_by_id(product_id)
        if not product:
            raise ProductNotFound(f"Product {product_id} not found")
        return product
