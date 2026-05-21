from app.domain.entities.order import Order
from app.domain.exceptions import OrderNotFound, Unauthorized
from app.domain.ports.order_repository import OrderRepository


class GetOrder:
    def __init__(self, repo: OrderRepository):
        self.repo = repo

    def execute(self, order_id: str, profile_id: str) -> Order:
        order = self.repo.get_by_id(order_id)
        if not order:
            raise OrderNotFound(f"Order {order_id} not found")
        if order.profile_id != profile_id:
            raise Unauthorized("Access denied")
        return order
