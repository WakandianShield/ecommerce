from app.domain.entities.order import OrderCreate, OrderItemCreate
from app.domain.errors import NotFoundError, ValidationError
from app.domain.ports.order_repository import OrderRepository
from app.domain.ports.product_repository import ProductRepository


class OrderService:
    def __init__(self, repo: OrderRepository, product_repo: ProductRepository) -> None:
        self._repo = repo
        self._product_repo = product_repo

    def create_order(self, profile_id: str, shipping_address: str, items: list[OrderItemCreate]):
        if not shipping_address.strip():
            raise ValidationError("Shipping address is required")
        if not items:
            raise ValidationError("Order must include items")
        product_quantities: dict[str, int] = {}
        for item in items:
            if item.quantity <= 0:
                raise ValidationError("Item quantity must be greater than zero")
            if item.unit_price_cents < 0:
                raise ValidationError("Item price must be zero or positive")
            if not item.name.strip():
                raise ValidationError("Item name is required")
            if not item.product_id or not item.product_id.strip():
                raise ValidationError("Product id is required")
            product_quantities[item.product_id] = product_quantities.get(item.product_id, 0) + item.quantity
        for product_id, quantity in product_quantities.items():
            product = self._product_repo.get(product_id)
            if not product:
                raise ValidationError(f"Product not found: {product_id}")
            if product.stock < quantity:
                raise ValidationError(f"Insufficient stock for product {product_id}")
        order = OrderCreate(profile_id=profile_id, shipping_address=shipping_address, items=items)
        return self._repo.create(order)

    def list_orders(self, profile_id: str):
        return self._repo.list_for_profile(profile_id)

    def get_order(self, profile_id: str, order_id: str):
        order = self._repo.get_for_profile(profile_id, order_id)
        if not order:
            raise NotFoundError("Order not found")
        return order

    def update_status(self, profile_id: str, order_id: str, status: str):
        if not status.strip():
            raise ValidationError("Status is required")
        order = self._repo.update_status(profile_id, order_id, status)
        if not order:
            raise NotFoundError("Order not found")
        return order
