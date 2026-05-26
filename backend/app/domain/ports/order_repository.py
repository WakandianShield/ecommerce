from typing import Protocol, List, Optional

from app.domain.entities.order import Order, OrderCreate


class OrderRepository(Protocol):
    def create(self, data: OrderCreate) -> Order:
        ...

    def list_for_profile(self, profile_id: str) -> List[Order]:
        ...

    def list_all(self) -> List[Order]:
        ...

    def get_for_profile(self, profile_id: str, order_id: str) -> Optional[Order]:
        ...

    def get(self, order_id: str) -> Optional[Order]:
        ...

    def update_status(self, profile_id: str, order_id: str, status: str) -> Optional[Order]:
        ...

    def update_status_any(self, order_id: str, status: str) -> Optional[Order]:
        ...
