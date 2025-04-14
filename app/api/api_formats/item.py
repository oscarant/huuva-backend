from typing import List, Optional
from uuid import UUID

from pydantic import Field

from app.api.api_formats.base import BaseSchema, OrmSchema
from app.api.api_formats.item_status import ItemStatus, ItemStatusHistory


class ItemCreate(BaseSchema):
    plu: str
    name: str
    quantity: int = Field(
        ...,
        ge=1,  # Assuming quantity should be a positive integer
        description="Quantity of the item",
    )
    status: Optional[ItemStatus] = ItemStatus.ORDERED


class Item(OrmSchema):
    id: UUID
    plu: str
    name: str
    quantity: int = Field(
        ...,
        ge=1,  # Assuming quantity should be a positive integer
        description="Quantity of the item",
    )
    status: ItemStatus
    status_history: List[ItemStatusHistory]
