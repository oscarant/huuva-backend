from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.core.entities.base import BaseSchema, OrmSchema
from app.core.entities.item import Item, ItemCreate
from app.core.entities.order_status import (
    OrderStatus,
    OrderStatusHistory,
    OrderStatusHistoryCreate,
)


class DeliveryAddress(BaseSchema):
    city: str
    street: str
    postal_code: str


class OrderCreate(BaseSchema):
    account: UUID
    brand_id: UUID
    channel_order_id: str
    customer_name: str
    customer_phone: str
    pickup_time: datetime
    status: OrderStatus
    delivery_address: DeliveryAddress
    items: List[ItemCreate]
    status_history: Optional[List[OrderStatusHistoryCreate]] = None


class OrderUpdate(BaseSchema):
    status: OrderStatus


class Order(OrmSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime
    account: UUID
    brand_id: UUID
    channel_order_id: str
    customer_name: str
    customer_phone: str
    pickup_time: datetime
    status: OrderStatus
    delivery_address: DeliveryAddress
    items: List[Item]
    status_history: List[OrderStatusHistory]
