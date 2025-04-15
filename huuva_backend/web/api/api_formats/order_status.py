from datetime import datetime
from enum import Enum

from huuva_backend.web.api.api_formats.base import OrmSchema


class OrderStatus(Enum):
    RECEIVED = 1
    PREPARING = 2
    READY = 3
    PICKED_UP = 4
    CANCELLED = 5

    def __str__(self) -> str:
        return self.name


class OrderStatusHistory(OrmSchema):
    status: OrderStatus
    timestamp: datetime
