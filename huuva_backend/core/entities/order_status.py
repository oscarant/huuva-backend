from datetime import datetime
from enum import IntEnum

from huuva_backend.core.entities.base import BaseSchema, OrmSchema


class OrderStatus(IntEnum):
    RECEIVED = 1
    PREPARING = 2
    READY = 3
    PICKED_UP = 4
    CANCELLED = 5


class OrderStatusHistoryCreate(BaseSchema):
    status: OrderStatus
    timestamp: datetime


class OrderStatusHistory(OrmSchema):
    status: OrderStatus
    timestamp: datetime
