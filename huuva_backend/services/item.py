from dataclasses import dataclass

from huuva_backend.core.entities.item import Item, ItemUpdate
from huuva_backend.db.repositories.item import ItemRepository


@dataclass
class ItemService:
    """
    Service layer for managing items within orders.

    This service provides methods to retrieve and update items.
    It interacts with the ItemRepository to perform database operations.
    """

    item_repository: ItemRepository

    async def get(self, order_id: str, plu: str) -> Item:
        """
        Retrieve an Item by its PLU code within a specific Order.

        Assumes that each order has unique PLU values for its items.
        Raises NotFoundError if the item is not found.
        """
        return Item.model_validate(
            await self.item_repository.get(order_id, plu),
        )

    async def update(self, order_id: str, plu: str, item_update: ItemUpdate) -> Item:
        """
        Atomically update the status of an individual order item and log the change.

        The logic of the logging is handled in the repository, but it should be
        here. I decided to keep the logic in the repository for practicability reasons.
        """
        return Item.model_validate(
            await self.item_repository.update(order_id, plu, item_update),
        )
