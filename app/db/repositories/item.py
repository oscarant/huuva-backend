from dataclasses import dataclass
from datetime import datetime, timezone
from typing import cast
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.entities.item import ItemUpdate
from app.db.models.item import Item as ItemModel
from app.db.models.item_status import ItemStatusHistory as ItemStatusHistoryModel
from app.exceptions.exceptions import NotFoundError


@dataclass
class ItemRepository:
    db: Session

    def get(self, order_id: UUID, plu: str) -> ItemModel:
        """
        Retrieve an Item by its PLU code within a specific Order.
        Assumes that each order has unique PLU values for its items.
        Raises NotFoundError if the item is not found.
        Uses SQLAlchemy's Session.get() as the model is defined with a composite PK.
        """
        # If your Item model uses a composite primary key (order_id, plu),
        # you can fetch the item like this:
        item = self.db.get(ItemModel, (order_id, plu))
        if not item:
            raise NotFoundError("Item", f"{order_id}:{plu}")
        return cast(ItemModel, item)

    def update(self, order_id: UUID, plu: UUID, item_update: ItemUpdate) -> ItemModel:
        """
        Atomically update the status of an individual order item and log the change.
        Acquires a row-level lock to avoid concurrency issues.
        Raises NotFoundError if the item is not found.
        """
        item = (
            self.db.query(ItemModel)
            .filter(ItemModel.order_id == order_id, ItemModel.plu == plu)
            .with_for_update()
            .one_or_none()
        )
        if not item:
            raise NotFoundError("Item", f"{order_id}:{plu}")
        item.status = item_update.status
        history_entry = ItemStatusHistoryModel(
            status=item_update.status,
            timestamp=datetime.now(timezone.utc),
        )
        item.status_history.append(history_entry)
        self.db.commit()
        self.db.refresh(item)
        return cast(ItemModel, item)
