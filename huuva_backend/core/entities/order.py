from datetime import datetime
from typing import List, Optional
from uuid import UUID

from huuva_backend.core.entities.base import BaseSchema, OrmSchema
from huuva_backend.core.entities.item import Item, ItemCreate
from huuva_backend.core.entities.order_status import (
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
    status: OrderStatus  # TODO: Ensure returning the status name
    status_history: List[OrderStatusHistory]


class OrderUpdate(BaseSchema):
    status: OrderStatus


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
    status: OrderStatus  # TODO: Ensure returning the status name
    status_history: List[OrderStatusHistory]
