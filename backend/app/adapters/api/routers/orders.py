from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.adapters.api.dependencies import get_current_profile, get_db
from app.adapters.api.schemas import OrderCreateIn, OrderOut, OrderStatusUpdateIn
from app.application.use_cases.order_service import OrderService
from app.domain.entities.order import OrderItemCreate
from app.domain.errors import NotFoundError, ValidationError
from app.infrastructure.database.repositories import SqlAlchemyOrderRepository


router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreateIn,
    profile=Depends(get_current_profile),
    db: Session = Depends(get_db),
):
    service = OrderService(SqlAlchemyOrderRepository(db))
    items = [
        OrderItemCreate(
            product_id=item.product_id,
            name=item.name,
            unit_price_cents=item.unit_price_cents,
            quantity=item.quantity,
        )
        for item in payload.items
    ]
    try:
        order = service.create_order(profile.id, payload.shipping_address, items)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return OrderOut.model_validate(order)


@router.get("", response_model=list[OrderOut])
def list_orders(profile=Depends(get_current_profile), db: Session = Depends(get_db)):
    service = OrderService(SqlAlchemyOrderRepository(db))
    orders = service.list_orders(profile.id)
    return [OrderOut.model_validate(order) for order in orders]


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: str, profile=Depends(get_current_profile), db: Session = Depends(get_db)):
    service = OrderService(SqlAlchemyOrderRepository(db))
    try:
        order = service.get_order(profile.id, order_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return OrderOut.model_validate(order)


@router.put("/{order_id}/status", response_model=OrderOut)
def update_status(
    order_id: str,
    payload: OrderStatusUpdateIn,
    profile=Depends(get_current_profile),
    db: Session = Depends(get_db),
):
    service = OrderService(SqlAlchemyOrderRepository(db))
    try:
        order = service.update_status(profile.id, order_id, payload.status)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return OrderOut.model_validate(order)
