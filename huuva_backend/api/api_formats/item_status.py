from datetime import datetime
from enum import Enum

from huuva_backend.api.api_formats.base import OrmSchema


class ItemStatus(Enum):
    ORDERED = 1
    PREPARING = 2
    READY = 3

    def __str__(self) -> str:
        return self.name


class ItemStatusHistory(OrmSchema):
    status: ItemStatus
    timestamp: datetime
