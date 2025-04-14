from dataclasses import dataclass
from typing import cast
from uuid import UUID

from app.core.entities.item import Item, ItemUpdate
from app.db.repositories.item import ItemRepository


@dataclass
class ItemService:
    item_repository: ItemRepository

    def get(self, order_id: UUID, plu: str) -> Item:
        """
        Retrieve an Item by its PLU code within a specific Order.
        Assumes that each order has unique PLU values for its items.
        Raises NotFoundError if the item is not found.
        """
        # Use model validate
        item = Item.model_validate(
            self.item_repository.get(order_id, plu),
        )
        return cast(Item, item)

    def update(self, order_id: UUID, plu: str, item_update: ItemUpdate) -> Item:
        """
        Atomically update the status of an individual order item and log the change.
        The logic of the logging is handled in the repository, but it should be
        here. I decided to keep the logic in the repository for practicability reasons.
        """
        return self.item_repository.update(order_id, plu, item_update)
