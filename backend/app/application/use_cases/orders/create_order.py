import uuid
from typing import List

from app.domain.entities.order import Order, OrderItem
from app.domain.exceptions import Unauthorized
from app.domain.ports.order_repository import OrderRepository


class OrderItemInput:
    def __init__(self, name: str, price: float, qty: int, img: str):
        self.name = name
        self.price = price
        self.qty = qty
        self.img = img


class CreateOrder:
    def __init__(self, repo: OrderRepository):
        self.repo = repo

    def execute(
        self,
        profile_id: str,
        items: List[OrderItemInput],
        shipping_address: str,
        total_cents: int,
    ) -> Order:
        if not profile_id:
            raise Unauthorized("Authentication required to place an order")

        order_id = str(uuid.uuid4())
        order_items = [
            OrderItem(
                id=str(uuid.uuid4()),
                order_id=order_id,
                product_name=item.name,
                quantity=item.qty,
                unit_price_cents=int(item.price * 100),
                image_url=item.img,
            )
            for item in items
        ]

        order = Order(
            id=order_id,
            profile_id=profile_id,
            status="confirmed",
            shipping_address=shipping_address,
            total_cents=total_cents,
            items=order_items,
        )
        return self.repo.save(order)
