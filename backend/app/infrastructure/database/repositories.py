from typing import List, Optional
import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.entities.order import Order, OrderCreate, OrderItem
from app.domain.entities.product import Product, ProductCreate, ProductUpdate
from app.domain.entities.profile import Profile, ProfileAuth
from app.domain.entities.refresh_token import RefreshToken
from app.domain.errors import ValidationError
from app.infrastructure.database.models import (
    OrderItemModel,
    OrderModel,
    ProductModel,
    ProfileModel,
    RefreshTokenModel,
)


class SqlAlchemyProductRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(self) -> List[Product]:
        products = self._session.execute(select(ProductModel)).scalars().all()
        return [self._to_entity(p) for p in products]

    def get(self, product_id: str) -> Optional[Product]:
        product = self._session.get(ProductModel, product_id)
        return self._to_entity(product) if product else None

    def create(self, data: ProductCreate) -> Product:
        model = ProductModel(
            id=str(uuid.uuid4()),
            name=data.name,
            description=data.description,
            price_cents=data.price_cents,
            stock=data.stock,
            category=data.category,
            image_url=data.image_url,
            is_active=data.is_active,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def update(self, product_id: str, data: ProductUpdate) -> Optional[Product]:
        model = self._session.get(ProductModel, product_id)
        if not model:
            return None
        if data.name is not None:
            model.name = data.name
        if data.description is not None:
            model.description = data.description
        if data.price_cents is not None:
            model.price_cents = data.price_cents
        if data.stock is not None:
            model.stock = data.stock
        if data.category is not None:
            model.category = data.category
        if data.image_url is not None:
            model.image_url = data.image_url
        if data.is_active is not None:
            model.is_active = data.is_active
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def decrement_stock(self, product_quantities: dict[str, int]) -> None:
        for product_id, quantity in product_quantities.items():
            model = self._session.get(ProductModel, product_id)
            if not model:
                raise ValidationError(f"Product not found: {product_id}")
            if model.stock < quantity:
                raise ValidationError(
                    f"Stock insuficiente para {model.name}. Disponible: {model.stock}."
                )
            model.stock -= quantity
        self._session.flush()

    def delete(self, product_id: str) -> bool:
        model = self._session.get(ProductModel, product_id)
        if not model:
            return False
        self._session.delete(model)
        self._session.commit()
        return True

    @staticmethod
    def _to_entity(model: ProductModel) -> Product:
        return Product(
            id=model.id,
            name=model.name,
            description=model.description,
            price_cents=model.price_cents,
            stock=model.stock,
            category=model.category,
            image_url=model.image_url,
            is_active=model.is_active,
        )


class SqlAlchemyProfileRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, profile_id: str) -> Optional[Profile]:
        model = self._session.get(ProfileModel, profile_id)
        return self._to_entity(model) if model else None

    def get_by_email(self, email: str) -> Optional[Profile]:
        stmt = select(ProfileModel).where(ProfileModel.email == email)
        model = self._session.execute(stmt).scalars().first()
        return self._to_entity(model) if model else None

    def get_auth_by_email(self, email: str) -> Optional[ProfileAuth]:
        stmt = select(ProfileModel).where(ProfileModel.email == email)
        model = self._session.execute(stmt).scalars().first()
        if not model:
            return None
        return ProfileAuth(
            id=model.id,
            full_name=model.full_name,
            email=model.email,
            role=model.role,
            password_hash=model.password_hash,
        )

    def create(self, full_name: str, email: str, password_hash: str, role: str) -> Profile:
        model = ProfileModel(
            id=str(uuid.uuid4()),
            full_name=full_name,
            email=email,
            password_hash=password_hash,
            role=role,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: ProfileModel) -> Profile:
        return Profile(id=model.id, full_name=model.full_name, email=model.email, role=model.role)


class SqlAlchemyRefreshTokenRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, profile_id: str, token_id: str, expires_at):
        model = RefreshTokenModel(
            id=token_id,
            profile_id=profile_id,
            expires_at=expires_at,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def get(self, token_id: str) -> Optional[RefreshToken]:
        model = self._session.get(RefreshTokenModel, token_id)
        return self._to_entity(model) if model else None

    def revoke(self, token_id: str) -> bool:
        model = self._session.get(RefreshTokenModel, token_id)
        if not model:
            return False
        model.revoked_at = func.now()
        self._session.commit()
        self._session.refresh(model)
        return True

    @staticmethod
    def _to_entity(model: RefreshTokenModel) -> RefreshToken:
        return RefreshToken(
            id=model.id,
            profile_id=model.profile_id,
            expires_at=model.expires_at,
            revoked_at=model.revoked_at,
        )


class SqlAlchemyOrderRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, data: OrderCreate) -> Order:
        total_cents = sum(item.unit_price_cents * item.quantity for item in data.items)
        order = OrderModel(
            id=str(uuid.uuid4()),
            profile_id=data.profile_id,
            status="created",
            total_cents=total_cents,
            shipping_address=data.shipping_address,
        )
        for item in data.items:
            order.items.append(
                OrderItemModel(
                    id=str(uuid.uuid4()),
                    order_id=order.id,
                    product_id=item.product_id,
                    name=item.name,
                    unit_price_cents=item.unit_price_cents,
                    quantity=item.quantity,
                )
            )
        self._session.add(order)
        self._session.commit()
        self._session.refresh(order)
        return self._to_entity(order)

    def list_for_profile(self, profile_id: str) -> List[Order]:
        stmt = select(OrderModel).where(OrderModel.profile_id == profile_id)
        orders = self._session.execute(stmt).scalars().all()
        return [self._to_entity(order) for order in orders]

    def list_all(self) -> List[Order]:
        orders = self._session.execute(select(OrderModel)).scalars().all()
        return [self._to_entity(order) for order in orders]

    def get_for_profile(self, profile_id: str, order_id: str) -> Optional[Order]:
        stmt = select(OrderModel).where(OrderModel.profile_id == profile_id, OrderModel.id == order_id)
        order = self._session.execute(stmt).scalars().first()
        return self._to_entity(order) if order else None

    def get(self, order_id: str) -> Optional[Order]:
        order = self._session.get(OrderModel, order_id)
        return self._to_entity(order) if order else None

    def update_status(self, profile_id: str, order_id: str, status: str) -> Optional[Order]:
        stmt = select(OrderModel).where(OrderModel.profile_id == profile_id, OrderModel.id == order_id)
        order = self._session.execute(stmt).scalars().first()
        if not order:
            return None
        order.status = status
        self._session.commit()
        self._session.refresh(order)
        return self._to_entity(order)

    def update_status_any(self, order_id: str, status: str) -> Optional[Order]:
        order = self._session.get(OrderModel, order_id)
        if not order:
            return None
        order.status = status
        self._session.commit()
        self._session.refresh(order)
        return self._to_entity(order)

    @staticmethod
    def _to_entity(model: OrderModel) -> Order:
        items = [
            OrderItem(
                id=item.id,
                product_id=item.product_id,
                name=item.name,
                unit_price_cents=item.unit_price_cents,
                quantity=item.quantity,
            )
            for item in model.items
        ]
        return Order(
            id=model.id,
            profile_id=model.profile_id,
            status=model.status,
            total_cents=model.total_cents,
            shipping_address=model.shipping_address,
            items=items,
        )
