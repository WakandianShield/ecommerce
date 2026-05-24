from app.domain.entities.product import ProductCreate, ProductUpdate
from app.domain.errors import NotFoundError, ValidationError
from app.domain.ports.product_repository import ProductRepository


class ProductService:
    def __init__(self, repo: ProductRepository) -> None:
        self._repo = repo

    def list_products(self):
        return self._repo.list()

    def get_product(self, product_id: str):
        product = self._repo.get(product_id)
        if not product:
            raise NotFoundError("Product not found")
        return product

    def create_product(self, data: ProductCreate):
        if data.price_cents <= 0:
            raise ValidationError("Price must be greater than zero")
        if data.stock < 0:
            raise ValidationError("Stock must be zero or positive")
        return self._repo.create(data)

    def update_product(self, product_id: str, data: ProductUpdate):
        if data.price_cents is not None and data.price_cents < 0:
            raise ValidationError("Price must be zero or positive")
        if data.stock is not None and data.stock < 0:
            raise ValidationError("Stock must be zero or positive")
        product = self._repo.update(product_id, data)
        if not product:
            raise NotFoundError("Product not found")
        return product

    def delete_product(self, product_id: str):
        deleted = self._repo.delete(product_id)
        if not deleted:
            raise NotFoundError("Product not found")
