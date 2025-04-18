from datetime import datetime
from typing import List, Optional

from pydantic import Field

from huuva_backend.web.api.api_formats.base import BaseSchema, OrmSchema
from huuva_backend.web.api.api_formats.item import Item, ItemCreate
from huuva_backend.web.api.api_formats.order_status import (
    OrderStatus,
    OrderStatusHistory,
)


class DeliveryAddress(BaseSchema):
    city: str
    street: str
    postal_code: str


class Customer(BaseSchema):
    name: str
    phone_number: str


# Replica of the OrderPayload from the example
class OrderCreate(BaseSchema):
    id: Optional[str] = Field(default=None, alias="_id")
    created: Optional[datetime] = None
    account: str
    brand_id: str
    channel_order_id: str
    customer: Customer
    delivery_address: DeliveryAddress
    pickup_time: datetime
    items: List[ItemCreate]
    status: OrderStatus
    status_history: List[OrderStatusHistory]


class OrderUpdate(BaseSchema):
    status: OrderStatus  # For updating overall order status


class Order(OrmSchema):
    id: str
    created_at: datetime
    updated_at: datetime
    account: str
    brand_id: str
    channel_order_id: str
    customer: Customer
    delivery_address: DeliveryAddress
    pickup_time: datetime
    items: List[Item]
    status: OrderStatus
    status_history: List[OrderStatusHistory]


class OrderQueryParams(BaseSchema):
    status: Optional[OrderStatus] = None
    account: Optional[str] = None
    from_date: Optional[datetime] = Field(None, alias="from")
    to_date: Optional[datetime] = Field(None, alias="to")
