from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from huuva_backend.core.entities.item import ItemUpdate
from huuva_backend.db.models.item import Item
from huuva_backend.db.models.item import Item as ItemModel
from huuva_backend.db.models.item_status import (
    ItemStatus as ItemStatusModel,
)
from huuva_backend.db.models.item_status import (
    ItemStatusHistory as ItemStatusHistoryModel,
)
from huuva_backend.exceptions.exceptions import NotFoundError


@dataclass
class ItemRepository:
    db: AsyncSession

    async def get(self, order_id: UUID, plu: str) -> ItemModel:
        """
        Retrieve an Item by its order ID and PLU code within a specific Order.

        Assumes that each order has unique (OrderID-PLU) values for its items.
        Raises NotFoundError if the item is not found.
        """

        result = await self.db.execute(self._get_item_query(order_id, plu))
        item = result.scalar_one_or_none()

        if not item:
            raise NotFoundError("Item", f"{order_id}:{plu}")

        return item

    async def update(
        self,
        order_id: UUID,
        plu: str,
        item_update: ItemUpdate,
    ) -> ItemModel:
        """
        Atomically update the status of an individual order item and log the change.

        Acquires a row-level lock to avoid concurrency issues.
        Raises NotFoundError if the item is not found.
        """

        # Acquire a row-level lock on the item to prevent concurrent updates
        result = await self.db.execute(
            self._get_item_query(order_id, plu).with_for_update(),
        )
        item = result.scalar_one_or_none()

        if not item:
            raise NotFoundError("Item", f"{order_id}:{plu}")

        # Convert entity enum to model enum
        item.status = ItemStatusModel(item_update.status.value)
        history_entry = ItemStatusHistoryModel(
            order_id=item.order_id,
            item_plu=item.plu,
            status=ItemStatusModel(item_update.status.value),
            timestamp=datetime.now(),
        )

        item.status_history.append(history_entry)

        await self.db.flush()
        await self.db.refresh(item, attribute_names=["status_history"])

        return item

    def _get_item_query(self, order_id: UUID, plu: str) -> Select[tuple[Item]]:
        """
        Helper method to construct a query for retrieving an item.

        This method is used internally to avoid code duplication.
        """

        return (
            select(ItemModel)
            .options(selectinload(ItemModel.status_history))
            .where(
                ItemModel.order_id == order_id,
                ItemModel.plu == plu,
            )
        )
