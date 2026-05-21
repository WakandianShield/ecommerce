from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.order import Order


class OrderRepository(ABC):
    @abstractmethod
    def get_by_id(self, order_id: str) -> Optional[Order]: ...

    @abstractmethod
    def get_by_profile(self, profile_id: str) -> List[Order]: ...

    @abstractmethod
    def save(self, order: Order) -> Order: ...
