from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from huuva_backend.core.entities.order import OrderCreate, OrderUpdate
from huuva_backend.db.mappings.order import order_create_to_db
from huuva_backend.db.models.item import Item as ItemModel
from huuva_backend.db.models.item_status import (
    ItemStatus as ItemStatusModel,
)
from huuva_backend.db.models.item_status import (
    ItemStatusHistory as ItemStatusHistoryModel,
)
from huuva_backend.db.models.order import Order
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
        # Check if the order already exists
        existing = await self.db.get(OrderModel, order_in.id)
        if existing:
            raise ConflictError("Order", str(order_in.id))

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
            await self.db.flush()
        except IntegrityError as e:
            await self.db.rollback()
            raise ConflictError("Order", str(order_in.id)) from e

        await self.db.refresh(order, attribute_names=["items", "status_history"])

        return order

    async def get(self, order_id: UUID) -> OrderModel:
        """
        Retrieve an Order by its UUID.

        Raises NotFoundError if not found.
        """
        result = await self.db.execute(self._get_order_query(order_id))
        order = result.scalar_one_or_none()

        if not order:
            raise NotFoundError("Order", str(order_id))

        return order

    async def update(self, order_id: UUID, order_update: OrderUpdate) -> OrderModel:
        """
        Atomically update the status of an Order and log the change.

        Uses a row-level lock to ensure concurrency safety.
        Raises NotFoundError if the Order is not found.
        """

        result = await self.db.execute(
            self._get_order_query(order_id).with_for_update(),
        )
        order = result.scalar_one_or_none()

        if not order:
            raise NotFoundError("Order", str(order_id))

        # Convert entity enum to model enum
        order.status = OrderStatusModel(order_update.status.value)

        history_entry = OrderStatusHistoryModel(
            order_id=order.id,
            status=OrderStatusModel(order_update.status.value),
            timestamp=datetime.now(),
        )

        # Create a new list if status_history doesn't exist yet
        if order.status_history is None:
            order.status_history = [history_entry]
        else:
            order.status_history.append(history_entry)

        await self.db.flush()

        await self.db.refresh(order, attribute_names=["status_history"])

        return order

    async def list(
        self,
        status: Optional[OrderStatusModel] = None,
        account: Optional[UUID] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> List[OrderModel]:
        """
        List orders with optional filtering.

        Args:
            status: Filter by order status
            account: Filter by account ID
            from_date: Filter orders created after this date
            to_date: Filter orders created before this date

        Returns:
            A list of Order models matching the filters
        """
        query = select(OrderModel).options(
            selectinload(OrderModel.items),
            selectinload(OrderModel.status_history),
        )

        if status is not None:
            query = query.where(OrderModel.status == status)

        if account is not None:
            query = query.where(OrderModel.account == account)

        if from_date is not None:
            query = query.where(OrderModel.created_at >= from_date)

        if to_date is not None:
            query = query.where(OrderModel.created_at <= to_date)

        # Order by creation date, newest first
        query = query.order_by(OrderModel.created_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

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
                order_id=order.id,
                item_plu=item_in.plu,
                status=status_value,
                timestamp=datetime.now(),
            )

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

    def _get_order_query(self, order_id: UUID) -> Select[tuple[Order]]:
        """Get the order query with the specified order ID."""
        return (
            select(OrderModel)
            .options(
                selectinload(OrderModel.items),
                selectinload(OrderModel.status_history),
            )
            .where(OrderModel.id == order_id)
        )
