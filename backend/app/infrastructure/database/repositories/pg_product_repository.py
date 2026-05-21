from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.entities.product import Product
from app.domain.ports.product_repository import ProductRepository
from app.infrastructure.database.models.product_model import ProductModel


class PgProductRepository(ProductRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[Product]:
        return [self._to_entity(m) for m in self.session.query(ProductModel).all()]

    def get_by_id(self, product_id: str) -> Optional[Product]:
        model = self.session.query(ProductModel).filter_by(id=product_id).first()
        return self._to_entity(model) if model else None

    def get_by_category(self, category: str) -> List[Product]:
        models = self.session.query(ProductModel).filter_by(category=category).all()
        return [self._to_entity(m) for m in models]

    def save(self, product: Product) -> Product:
        model = self.session.query(ProductModel).filter_by(id=product.id).first()
        if model:
            model.name = product.name
            model.artist = product.artist
            model.year = product.year
            model.price_cents = product.price_cents
            model.category = product.category
            model.image_url = product.image_url
            model.stock = product.stock
        else:
            model = ProductModel(
                id=product.id,
                name=product.name,
                artist=product.artist,
                year=product.year,
                price_cents=product.price_cents,
                category=product.category,
                image_url=product.image_url,
                stock=product.stock,
            )
            self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: ProductModel) -> Product:
        return Product(
            id=model.id,
            name=model.name,
            artist=model.artist,
            year=model.year,
            price_cents=model.price_cents,
            category=model.category,
            image_url=model.image_url,
            stock=model.stock,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
