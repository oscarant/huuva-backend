from datetime import datetime
from enum import IntEnum

from huuva_backend.core.entities.base import BaseSchema, OrmSchema


class ItemStatus(IntEnum):
    ORDERED = 1
    PREPARING = 2
    READY = 3


class ItemStatusHistoryCreate(BaseSchema):
    status: ItemStatus
    timestamp: datetime


class ItemStatusHistory(OrmSchema):
    status: ItemStatus
    timestamp: datetime
