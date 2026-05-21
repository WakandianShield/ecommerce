from app.domain.entities.order import OrderCreate, OrderItemCreate
from app.domain.errors import NotFoundError, ValidationError
from app.domain.ports.order_repository import OrderRepository


class OrderService:
    def __init__(self, repo: OrderRepository) -> None:
        self._repo = repo

    def create_order(self, profile_id: str, shipping_address: str, items: list[OrderItemCreate]):
        if not shipping_address.strip():
            raise ValidationError("Shipping address is required")
        if not items:
            raise ValidationError("Order must include items")
        for item in items:
            if item.quantity <= 0:
                raise ValidationError("Item quantity must be greater than zero")
            if item.unit_price_cents < 0:
                raise ValidationError("Item price must be zero or positive")
            if not item.name.strip():
                raise ValidationError("Item name is required")
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
