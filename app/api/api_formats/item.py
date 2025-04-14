from typing import List, Optional

from pydantic import Field, field_validator

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

    @field_validator("status", mode="before")
    def convert_status(cls, value):
        if isinstance(value, int):
            return ItemStatus(value)
        return value


class ItemUpdate(BaseSchema):
    status: ItemStatus

    @field_validator("status", mode="before")
    def convert_status(cls, value):
        if isinstance(value, int):
            return ItemStatus(value)
        return value


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

    @field_validator("status", mode="before")
    def convert_status(cls, value):
        if isinstance(value, int):
            return ItemStatus(value)
        return value
