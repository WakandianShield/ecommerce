import strawberry

from app.domain.entities.product import Product


@strawberry.type
class ProductType:
    id: strawberry.ID
    name: str
    artist: str
    year: int
    price_cents: int
    category: str
    image_url: str
    stock: int

    @classmethod
    def from_entity(cls, product: Product) -> "ProductType":
        return cls(
            id=product.id,
            name=product.name,
            artist=product.artist,
            year=product.year,
            price_cents=product.price_cents,
            category=product.category,
            image_url=product.image_url,
            stock=product.stock,
        )
