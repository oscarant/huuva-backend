from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from huuva_backend.core.entities.order import OrderCreate, OrderUpdate
from huuva_backend.db.mappings.order import order_create_to_db
from huuva_backend.db.models.item import Item as ItemModel
from huuva_backend.db.models.item_status import ItemStatus as ItemStatusModel
from huuva_backend.db.models.order import Order as OrderModel
from huuva_backend.db.models.order_status import (
    OrderStatus as OrderStatusModel,
)
from huuva_backend.db.models.order_status import (
    OrderStatusHistory as OrderStatusHistoryModel,
)
from huuva_backend.exceptions.exceptions import NotFoundError


@dataclass
class OrderRepository:
    db: AsyncSession

    async def create(self, order_in: OrderCreate) -> OrderModel:
        """
        Create a new Order (and associated items/status history) in the database.

        Assumptions:
            - The 'account' uniquely identifies a customer.
            - Delivery address fields are provided in the nested 'delivery_address'
            object.
        """
        order = order_create_to_db(order_in)

        # Create items for the order
        items: List[ItemModel] = []
        for item_in in order_in.items:
            # Handle potential None status safely
            status_value = ItemStatusModel.ORDERED
            if item_in.status is not None:
                status_value = ItemStatusModel(item_in.status.value)

            item = ItemModel(
                name=item_in.name,
                plu=item_in.plu,
                quantity=item_in.quantity,
                status=status_value,
            )
            items.append(item)

        order.items = items

        # Create initial order status history if provided
        if order_in.status_history:
            status_history: List[OrderStatusHistoryModel] = []
            for hist_in in order_in.status_history:
                history_entry = OrderStatusHistoryModel(
                    status=OrderStatusModel(hist_in.status.value),
                    timestamp=hist_in.timestamp,
                )
                status_history.append(history_entry)

            order.status_history = status_history

        self.db.add(order)
        await self.db.commit()
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
            # Use list to store, then assign back to the Mapped field
            current_history = list(order.status_history)
            current_history.append(history_entry)
            order.status_history = current_history

        await self.db.commit()
        await self.db.refresh(order)

        return order
