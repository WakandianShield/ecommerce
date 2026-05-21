from typing import List

import strawberry

from app.domain.entities.order import Order, OrderItem


@strawberry.type
class OrderItemType:
    id: strawberry.ID
    product_name: str
    quantity: int
    unit_price_cents: int
    image_url: str

    @classmethod
    def from_entity(cls, item: OrderItem) -> "OrderItemType":
        return cls(
            id=item.id,
            product_name=item.product_name,
            quantity=item.quantity,
            unit_price_cents=item.unit_price_cents,
            image_url=item.image_url,
        )


@strawberry.type
class OrderType:
    id: strawberry.ID
    profile_id: str
    status: str
    shipping_address: str
    total_cents: int
    items: List[OrderItemType]
    created_at: str

    @classmethod
    def from_entity(cls, order: Order) -> "OrderType":
        return cls(
            id=order.id,
            profile_id=order.profile_id,
            status=order.status,
            shipping_address=order.shipping_address,
            total_cents=order.total_cents,
            items=[OrderItemType.from_entity(i) for i in order.items],
            created_at=order.created_at.isoformat() if order.created_at else "",
        )
