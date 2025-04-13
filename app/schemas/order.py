from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from app.schemas.base import BaseSchema, OrmSchema


# Enums for statuses (mirroring model definitions)
class OrderStatus(Enum):
    RECEIVED = 1
    PREPARING = 2
    READY = 3
    PICKED_UP = 4
    CANCELLED = 5


class ItemStatus(Enum):
    ORDERED = 1
    PREPARING = 2
    READY = 3


class DeliveryAddress(BaseSchema):
    city: str
    street: str
    postal_code: str


class ItemCreate(BaseSchema):
    name: str
    plu: str
    quantity: int
    status: Optional[ItemStatus] = ItemStatus.ORDERED


class Item(OrmSchema):
    id: UUID
    name: str
    plu: str
    quantity: int
    status: ItemStatus


class OrderStatusHistoryCreate(BaseSchema):
    status: OrderStatus
    timestamp: datetime


class OrderStatusHistory(OrmSchema):
    id: UUID
    status: OrderStatus
    timestamp: datetime


# Schemas for item status history entries (if needed)
class ItemStatusHistoryCreate(BaseSchema):
    status: ItemStatus
    timestamp: datetime


class ItemStatusHistory(OrmSchema):
    id: UUID
    status: ItemStatus
    timestamp: datetime


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


class OrderStatusUpdate(BaseSchema):
    status: OrderStatus


class ItemStatusUpdate(BaseSchema):
    status: ItemStatus
