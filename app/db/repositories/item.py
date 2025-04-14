from dataclasses import dataclass
from datetime import datetime, timezone
from typing import cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.entities.item import ItemUpdate
from app.db.models.item import Item as ItemModel
from app.db.models.item_status import ItemStatusHistory as ItemStatusHistoryModel
from app.exceptions.exceptions import NotFoundError


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

        return cast(ItemModel, item)

    async def update(
        self, order_id: UUID, plu: str, item_update: ItemUpdate
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

        item.status = item_update.status
        history_entry = ItemStatusHistoryModel(
            status=item_update.status,
            timestamp=datetime.now(timezone.utc),
        )
        item.status_history.append(history_entry)

        await self.db.commit()
        await self.db.refresh(item)

        return cast(ItemModel, item)
