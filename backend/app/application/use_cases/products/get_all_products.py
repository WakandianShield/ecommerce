from typing import List

from app.domain.entities.product import Product
from app.domain.ports.product_repository import ProductRepository


class GetAllProducts:
    def __init__(self, repo: ProductRepository):
        self.repo = repo

    def execute(self) -> List[Product]:
        return self.repo.get_all()
