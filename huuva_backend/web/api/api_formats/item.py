from typing import List, Optional

from pydantic import Field

from huuva_backend.web.api.api_formats.base import BaseSchema, OrmSchema
from huuva_backend.web.api.api_formats.item_status import ItemStatus, ItemStatusHistory


class ItemCreate(BaseSchema):
    plu: str
    name: str
    quantity: int = Field(
        ...,
        ge=1,  # Assuming quantity should be a positive integer
        description="Quantity of the item",
    )
    status: Optional[ItemStatus] = ItemStatus.ORDERED


class ItemUpdate(BaseSchema):
    status: ItemStatus


class Item(OrmSchema):
    name: str
    plu: str
    quantity: int = Field(
        ...,
        ge=1,  # Assuming quantity should be a positive integer
        description="Quantity of the item",
    )
    status: ItemStatus
    status_history: List[ItemStatusHistory]
