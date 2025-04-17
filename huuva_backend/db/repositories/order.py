from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from huuva_backend.core.entities.order import OrderCreate, OrderUpdate
from huuva_backend.db.mappings.order import order_create_to_db
from huuva_backend.db.models.item import Item as ItemModel
from huuva_backend.db.models.item_status import (
    ItemStatus as ItemStatusModel,
)
from huuva_backend.db.models.item_status import (
    ItemStatusHistory as ItemStatusHistoryModel,
)
from huuva_backend.db.models.order import Order as OrderModel
from huuva_backend.db.models.order_status import (
    OrderStatus as OrderStatusModel,
)
from huuva_backend.db.models.order_status import (
    OrderStatusHistory as OrderStatusHistoryModel,
)
from huuva_backend.exceptions.exceptions import ConflictError, NotFoundError


@dataclass
class OrderRepository:
    db: AsyncSession

    async def create(self, order_in: OrderCreate) -> OrderModel:
        """
        Create a new Order (and associated items/status history) in the database.

        Assumptions:
            - The 'account' uniquely identifies a customer.
            - We are not receiving an item status and status history for the order.
        """
        order = order_create_to_db(order_in)

        # Create items for the order
        items: List[ItemModel] = self._create_items(order, order_in)
        order.items = items

        # Create status history for the order
        status_history: List[OrderStatusHistoryModel] = (
            self._create_order_status_history(
                order,
                order_in,
            )
        )
        order.status_history = status_history

        self.db.add(order)
        try:
            await self.db.commit()
        except Exception as e:
            # Handle unique constraint violation
            if "unique constraint" in str(e):
                raise ConflictError("Order", str(order_in.id)) from e
            raise e
        await self.db.refresh(order)

        return order

    async def get(self, order_id: UUID) -> OrderModel:
        """
        Retrieve an Order by its UUID.

        Raises NotFoundError if not found.
        """
        order = await self.db.get(OrderModel, order_id)

        if not order:
            raise NotFoundError("Order", str(order_id))

        return order

    async def update(self, order_id: UUID, order_update: OrderUpdate) -> OrderModel:
        """
        Atomically update the status of an Order and log the change.

        Uses a row-level lock to ensure concurrency safety.
        Raises NotFoundError if the Order is not found.
        """
        query = select(OrderModel).where(OrderModel.id == order_id).with_for_update()
        result = await self.db.execute(query)
        order = result.scalar_one_or_none()

        if not order:
            raise NotFoundError("Order", str(order_id))

        # Convert entity enum to model enum
        order.status = OrderStatusModel(order_update.status.value)

        history_entry = OrderStatusHistoryModel(
            status=OrderStatusModel(order_update.status.value),
            timestamp=datetime.now(timezone.utc),
        )

        # Create a new list if status_history doesn't exist yet
        if order.status_history is None:
            order.status_history = [history_entry]
        else:
            order.status_history.append(history_entry)

        await self.db.commit()
        await self.db.refresh(order)

        return order

    def _create_items(
        self,
        order: OrderModel,
        order_in: OrderCreate,
    ) -> List[ItemModel]:
        """Create items for the order. Also handles status history for each item."""
        items: List[ItemModel] = []
        for item_in in order_in.items:
            # Handle potential None status safely
            status_value = ItemStatusModel.ORDERED
            if item_in.status is not None:
                status_value = ItemStatusModel(item_in.status.value)

            item = ItemModel(
                order_id=order.id,
                plu=item_in.plu,
                name=item_in.name,
                quantity=item_in.quantity,
                status=status_value,
            )

            # Create history entry
            history_entry = ItemStatusHistoryModel(
                status=status_value,
                timestamp=datetime.now(timezone.utc),
            )
            # Let SQLAlchemy handle setting the foreign keys
            item.status_history = [history_entry]

            items.append(item)
        return items

    def _create_order_status_history(
        self,
        order: OrderModel,
        order_in: OrderCreate,
    ) -> List[OrderStatusHistoryModel]:
        """Create initial order status history if provided."""
        status_history: List[OrderStatusHistoryModel] = []
        for hist_in in order_in.status_history:
            history_entry = OrderStatusHistoryModel(
                order_id=order.id,
                status=OrderStatusModel(hist_in.status.value),
                timestamp=hist_in.timestamp,
            )
            status_history.append(history_entry)
        return status_history
