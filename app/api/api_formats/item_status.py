from datetime import datetime
from enum import Enum

from app.api.api_formats.base import OrmSchema


class ItemStatus(Enum):
    ORDERED = 1
    PREPARING = 2
    READY = 3


class ItemStatusHistory(OrmSchema):
    status: ItemStatus
    timestamp: datetime
