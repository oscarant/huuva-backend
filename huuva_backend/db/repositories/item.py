from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from huuva_backend.core.entities.item import ItemUpdate
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
        Retrieve an Item by its PLU code within a specific Order.

        Assumes that each order has unique PLU values for its items.
        Raises NotFoundError if the item is not found.
        """
        item = await self.db.get(ItemModel, (order_id, plu))

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
        query = (
            select(ItemModel)
            .where(ItemModel.order_id == order_id, ItemModel.plu == plu)
            .with_for_update()
        )
        result = await self.db.execute(query)
        item = result.scalar_one_or_none()

        if not item:
            raise NotFoundError("Item", f"{order_id}:{plu}")

        # Convert entity enum to model enum
        item.status = ItemStatusModel(item_update.status.value)
        history_entry = ItemStatusHistoryModel(
            status=ItemStatusModel(item_update.status.value),
            timestamp=datetime.now(timezone.utc),
        )
        item.status_history.append(history_entry)

        await self.db.commit()
        await self.db.refresh(item)

        return item
