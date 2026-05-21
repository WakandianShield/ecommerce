from typing import List

from app.domain.entities.order import Order
from app.domain.ports.order_repository import OrderRepository


class GetOrdersByProfile:
    def __init__(self, repo: OrderRepository):
        self.repo = repo

    def execute(self, profile_id: str) -> List[Order]:
        return self.repo.get_by_profile(profile_id)
