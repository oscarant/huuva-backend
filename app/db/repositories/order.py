from dataclasses import dataclass
from datetime import datetime, timezone
from typing import cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.entities.order import OrderCreate, OrderUpdate
from app.db.mappings.order import order_create_to_db
from app.db.models.item import Item as ItemModel
from app.db.models.order import Order as OrderModel
from app.db.models.order_status import OrderStatusHistory as OrderStatusHistoryModel
from app.exceptions.exceptions import NotFoundError


@dataclass
class OrderRepository:
    db: AsyncSession

    async def create(self, order_in: OrderCreate) -> OrderModel:
        """
        Create a new Order (and associated items/status history) in the database.
        Assumptions:
            - The 'account' uniquely identifies a customer.
            - Delivery address fields are provided in the nested 'delivery_address' object.
        """
        order = order_create_to_db(order_in)

        # Create items for the order
        order.items = []
        for item_in in order_in.items:
            item = ItemModel(
                name=item_in.name,
                plu=item_in.plu,
                quantity=item_in.quantity,
                status=item_in.status,
            )
            order.items.append(item)

        # Create initial order status history if provided
        if order_in.status_history:
            order.status_history = []
            for hist_in in order_in.status_history:
                history_entry = OrderStatusHistoryModel(
                    status=hist_in.status,
                    timestamp=hist_in.timestamp,
                )
                order.status_history.append(history_entry)

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

        return cast(OrderModel, order)

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

        order.status = order_update.status

        history_entry = OrderStatusHistoryModel(
            status=order_update.status,
            timestamp=datetime.now(timezone.utc),
        )
        order.status_history.append(history_entry)

        await self.db.commit()
        await self.db.refresh(order)

        return cast(OrderModel, order)
