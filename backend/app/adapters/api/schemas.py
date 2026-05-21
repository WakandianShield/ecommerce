from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ProductCreateIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: Optional[str] = None
    price_cents: int = Field(ge=0)
    stock: int = Field(ge=0)
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True


class ProductUpdateIn(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    description: Optional[str] = None
    price_cents: Optional[int] = Field(default=None, ge=0)
    stock: Optional[int] = Field(default=None, ge=0)
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: Optional[str]
    price_cents: int
    stock: int
    category: Optional[str]
    image_url: Optional[str]
    is_active: bool


class ProfileCreateIn(BaseModel):
    full_name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class ProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    full_name: str
    email: EmailStr


class SessionIn(BaseModel):
    email: EmailStr
    password: str


class SessionOut(BaseModel):
    token: str
    profile: ProfileOut


class OrderItemIn(BaseModel):
    product_id: Optional[str] = None
    name: str = Field(min_length=1, max_length=160)
    unit_price_cents: int = Field(ge=0)
    quantity: int = Field(ge=1)


class OrderCreateIn(BaseModel):
    shipping_address: str = Field(min_length=1, max_length=240)
    items: List[OrderItemIn]


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    product_id: Optional[str]
    name: str
    unit_price_cents: int
    quantity: int


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    profile_id: str
    status: str
    total_cents: int
    shipping_address: str
    items: List[OrderItemOut]


class OrderStatusUpdateIn(BaseModel):
    status: str = Field(min_length=1, max_length=40)
