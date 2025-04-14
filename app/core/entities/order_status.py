from datetime import datetime
from enum import Enum
from uuid import UUID

from app.core.entities.base import BaseSchema, OrmSchema


class OrderStatus(Enum):
    RECEIVED = 1
    PREPARING = 2
    READY = 3
    PICKED_UP = 4
    CANCELLED = 5


class OrderStatusHistoryCreate(BaseSchema):
    status: OrderStatus
    timestamp: datetime


class OrderStatusHistory(OrmSchema):
    id: UUID
    status: OrderStatus
    timestamp: datetime
