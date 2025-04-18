from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from huuva_backend.core.entities.item import ItemUpdate as ItemUpdateModel
from huuva_backend.core.entities.item_status import ItemStatus as ItemStatusModel
from huuva_backend.core.entities.order import Order, OrderCreate, OrderUpdate
from huuva_backend.core.entities.order_status import OrderStatus
from huuva_backend.db.mappings.order import order_db_to_entity
from huuva_backend.db.models.order import OrderStatus as OrderStatusModel
from huuva_backend.db.repositories.item import ItemRepository
from huuva_backend.db.repositories.order import OrderRepository


@dataclass
class OrderService:
    """
    Service class for handling order-related operations.

    This class is responsible for creating, updating, and retrieving orders.
    It interacts with the OrderRepository to perform database operations.
    """

    order_repository: OrderRepository
    item_repository: ItemRepository

    async def create_order(self, order_in: OrderCreate) -> Order:
        """
        Create a new order in the database.

        This method takes an OrderCreate object, maps it to the database model,
        and uses the repository to persist it. Returns the created order.
        """
        order = await self.order_repository.create(order_in)

        return order_db_to_entity(order)

    async def get_order(self, order_id: str) -> Order:
        """
        Retrieve an order by its unique ID.

        This method uses the repository to fetch the order from the database.
        Raises NotFoundError if the order is not found.
        """
        order = await self.order_repository.get(order_id)

        return order_db_to_entity(order)

    async def list_orders(
        self,
        status: Optional[OrderStatus] = None,
        account: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> list[Order]:
        """
        List orders based on filtering criteria.

        This method allows filtering orders by status, account, and date range.
        It returns a list of orders that match the criteria.
        """
        orders = await self.order_repository.list(
            OrderStatusModel(status.value) if status else None,
            account,
            from_date,
            to_date,
        )

        return [order_db_to_entity(order) for order in orders]

    async def update_order(self, order_id: str, order_update: OrderUpdate) -> Order:
        """
        Update the status of an order. Also updates the items in the order.

        This method takes an OrderUpdate object, which contains the new status,
        and uses the repository to update the order in the database.
        """
        order = await self.order_repository.update(order_id, order_update)

        # Update the status of items in the order to the new status
        for item in order.items:
            item_update = ItemUpdateModel(
                status=ItemStatusModel(order_update.status.value),
            )
            await self.item_repository.update(order_id, item.plu, item_update)

        return await self.get_order(order_id)
