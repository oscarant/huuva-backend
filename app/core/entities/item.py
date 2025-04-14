from typing import List, Optional
from uuid import UUID

from pydantic import Field

from app.core.entities.base import BaseSchema, OrmSchema
from app.core.entities.item_status import ItemStatus


class ItemCreate(BaseSchema):
    name: str
    plu: str
    quantity: int = Field(
        ...,
        ge=1,  # Assuming quantity should be a positive integer
        description="Quantity of the item",
    )
    status: Optional[ItemStatus] = ItemStatus.ORDERED


class ItemUpdate(BaseSchema):
    status: ItemStatus


class Item(OrmSchema):
    id: UUID
    name: str
    plu: str
    quantity: int
    status: ItemStatus
    status_history: List[ItemStatus]
