from datetime import datetime
from typing import List, Optional
from uuid import UUID

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
    id: Optional[UUID] = None
    created: Optional[datetime] = None
    account: UUID
    brand_id: UUID
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
    id: UUID
    created_at: datetime
    updated_at: datetime
    account: UUID
    brand_id: UUID
    channel_order_id: str
    customer: Customer
    delivery_address: DeliveryAddress
    pickup_time: datetime
    items: List[Item]
    status: OrderStatus
    status_history: List[OrderStatusHistory]


class OrderQueryParams(BaseSchema):
    status: Optional[OrderStatus] = None
    account: Optional[UUID] = None
    from_date: Optional[datetime] = Field(None, alias="from")
    to_date: Optional[datetime] = Field(None, alias="to")
