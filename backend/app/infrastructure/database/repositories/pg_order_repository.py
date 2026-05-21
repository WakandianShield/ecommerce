from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.entities.order import Order, OrderItem
from app.domain.ports.order_repository import OrderRepository
from app.infrastructure.database.models.order_model import OrderItemModel, OrderModel


class PgOrderRepository(OrderRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, order_id: str) -> Optional[Order]:
        model = self.session.query(OrderModel).filter_by(id=order_id).first()
        return self._to_entity(model) if model else None

    def get_by_profile(self, profile_id: str) -> List[Order]:
        models = self.session.query(OrderModel).filter_by(profile_id=profile_id).all()
        return [self._to_entity(m) for m in models]

    def save(self, order: Order) -> Order:
        model = OrderModel(
            id=order.id,
            profile_id=order.profile_id,
            status=order.status,
            shipping_address=order.shipping_address,
            total_cents=order.total_cents,
            items=[
                OrderItemModel(
                    id=item.id,
                    order_id=item.order_id,
                    product_name=item.product_name,
                    quantity=item.quantity,
                    unit_price_cents=item.unit_price_cents,
                    image_url=item.image_url,
                )
                for item in order.items
            ],
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: OrderModel) -> Order:
        return Order(
            id=model.id,
            profile_id=model.profile_id,
            status=model.status,
            shipping_address=model.shipping_address,
            total_cents=model.total_cents,
            items=[
                OrderItem(
                    id=item.id,
                    order_id=item.order_id,
                    product_name=item.product_name,
                    quantity=item.quantity,
                    unit_price_cents=item.unit_price_cents,
                    image_url=item.image_url,
                )
                for item in model.items
            ],
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
