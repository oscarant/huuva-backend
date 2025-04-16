from typing import Any, List, Optional

from pydantic import Field, field_validator

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

    @classmethod
    @field_validator("status", mode="before")
    def convert_status(cls, value: Any) -> ItemStatus:  # noqa
        if isinstance(value, int):
            return ItemStatus(value)
        return value


class ItemUpdate(BaseSchema):
    status: ItemStatus

    @classmethod
    @field_validator("status", mode="before")
    def convert_status(cls, value: Any) -> ItemStatus:  # noqa
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

    @classmethod
    @field_validator("status", mode="before")
    def convert_status(cls, value: Any) -> ItemStatus:  # noqa
        if isinstance(value, int):
            return ItemStatus(value)
        return value
