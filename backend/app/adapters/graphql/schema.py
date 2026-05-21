from typing import List, Optional

import strawberry
from strawberry.types import Info

from app.adapters.graphql.types.order_type import OrderType
from app.adapters.graphql.types.product_type import ProductType
from app.adapters.graphql.types.profile_type import AuthPayloadType, UserProfileType
from app.application.use_cases.orders.create_order import CreateOrder, OrderItemInput
from app.application.use_cases.orders.get_order import GetOrder
from app.application.use_cases.orders.get_orders_by_profile import GetOrdersByProfile
from app.application.use_cases.products.get_all_products import GetAllProducts
from app.application.use_cases.products.get_product_by_id import GetProductById
from app.application.use_cases.products.get_products_by_category import GetProductsByCategory
from app.application.use_cases.profiles.get_profile import GetProfile
from app.application.use_cases.profiles.login_profile import LoginProfile
from app.application.use_cases.profiles.register_profile import RegisterProfile
from app.domain.exceptions import (
    DomainException,
    InvalidCredentials,
    ProfileAlreadyExists,
    Unauthorized,
)
from app.infrastructure.auth.jwt_handler import (
    PasswordHasher,
    create_access_token,
    decode_access_token,
)
from app.infrastructure.database.repositories.pg_order_repository import PgOrderRepository
from app.infrastructure.database.repositories.pg_product_repository import PgProductRepository
from app.infrastructure.database.repositories.pg_profile_repository import PgProfileRepository

_hasher = PasswordHasher()


@strawberry.input
class OrderItemInputType:
    name: str
    price: float
    qty: int
    img: str


@strawberry.type
class Query:
    @strawberry.field
    def products(self, info: Info, category: Optional[str] = None) -> List[ProductType]:
        db = info.context["db"]
        repo = PgProductRepository(db)
        if category:
            results = GetProductsByCategory(repo).execute(category)
        else:
            results = GetAllProducts(repo).execute()
        return [ProductType.from_entity(p) for p in results]

    @strawberry.field
    def product(self, info: Info, id: strawberry.ID) -> Optional[ProductType]:
        db = info.context["db"]
        repo = PgProductRepository(db)
        try:
            p = GetProductById(repo).execute(str(id))
            return ProductType.from_entity(p)
        except DomainException:
            return None

    @strawberry.field
    def me(self, info: Info) -> Optional[UserProfileType]:
        profile_id = info.context.get("profile_id")
        if not profile_id:
            return None
        db = info.context["db"]
        repo = PgProfileRepository(db)
        try:
            profile = GetProfile(repo).execute(profile_id)
            return UserProfileType.from_entity(profile)
        except DomainException:
            return None

    @strawberry.field
    def orders(self, info: Info) -> List[OrderType]:
        profile_id = info.context.get("profile_id")
        if not profile_id:
            return []
        db = info.context["db"]
        repo = PgOrderRepository(db)
        results = GetOrdersByProfile(repo).execute(profile_id)
        return [OrderType.from_entity(o) for o in results]

    @strawberry.field
    def order(self, info: Info, id: strawberry.ID) -> Optional[OrderType]:
        profile_id = info.context.get("profile_id")
        if not profile_id:
            return None
        db = info.context["db"]
        repo = PgOrderRepository(db)
        try:
            o = GetOrder(repo).execute(str(id), profile_id)
            return OrderType.from_entity(o)
        except DomainException:
            return None


@strawberry.type
class Mutation:
    @strawberry.mutation
    def login(self, info: Info, email: str, password: str) -> AuthPayloadType:
        db = info.context["db"]
        repo = PgProfileRepository(db)
        try:
            profile = LoginProfile(repo, _hasher).execute(email, password)
        except InvalidCredentials as e:
            raise Exception(str(e))
        token = create_access_token(profile.id, profile.email)
        return AuthPayloadType(
            token=token,
            user=UserProfileType.from_entity(profile),
        )

    @strawberry.mutation
    def register(self, info: Info, full_name: str, email: str, password: str) -> AuthPayloadType:
        db = info.context["db"]
        repo = PgProfileRepository(db)
        try:
            profile = RegisterProfile(repo, _hasher).execute(full_name, email, password)
        except ProfileAlreadyExists as e:
            raise Exception(str(e))
        token = create_access_token(profile.id, profile.email)
        return AuthPayloadType(
            token=token,
            user=UserProfileType.from_entity(profile),
        )

    @strawberry.mutation
    def create_order_from_items(
        self,
        info: Info,
        items: List[OrderItemInputType],
        shipping_address: str,
        total_cents: int,
    ) -> OrderType:
        profile_id = info.context.get("profile_id")
        if not profile_id:
            raise Exception("Authentication required")
        db = info.context["db"]
        repo = PgOrderRepository(db)
        input_items = [OrderItemInput(i.name, i.price, i.qty, i.img) for i in items]
        try:
            order = CreateOrder(repo).execute(profile_id, input_items, shipping_address, total_cents)
        except Unauthorized as e:
            raise Exception(str(e))
        return OrderType.from_entity(order)


schema = strawberry.Schema(query=Query, mutation=Mutation)
