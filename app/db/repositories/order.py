from dataclasses import dataclass
from datetime import datetime, timezone
from typing import cast

from sqlalchemy.orm import Session

from app.core.entities.order import OrderCreate
from app.db.models.item import Item as ItemModel
from app.db.models.order import Order as OrderModel
from app.db.models.order import (
    OrderStatus,
)
from app.db.models.order_status import OrderStatusHistory as OrderStatusHistoryModel
from app.exceptions.exceptions import NotFoundError


@dataclass
class OrderRepository:
    db: Session

    def create_order(self, order_in: OrderCreate) -> OrderModel:
        """
        Create a new Order (and associated items/status history) in the database.
        Assumptions:
            - The 'account' uniquely identifies a customer.
            - Delivery address fields are provided in the nested 'delivery_address' object.
        """
        order = OrderModel(
            account=order_in.account,
            brand_id=order_in.brand_id,
            channel_order_id=order_in.channel_order_id,
            customer_name=order_in.customer_name,
            customer_phone=order_in.customer_phone,
            pickup_time=order_in.pickup_time,
            status=order_in.status,  # assuming the schema value is already of type OrderStatus
            delivery_city=order_in.delivery_address.city,
            delivery_street=order_in.delivery_address.street,
            delivery_postal_code=order_in.delivery_address.postal_code,
        )

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
        self.db.commit()
        self.db.refresh(order)
        return order

    def get_order(self, order_id: str) -> OrderModel:
        """
        Retrieve an Order by its UUID.
        Raises NotFoundError if not found.
        """
        order = self.db.get(OrderModel, order_id)
        if not order:
            raise NotFoundError("Order", order_id)
        return cast(OrderModel, order)

    def update_order_status(self, order_id: str, new_status: OrderStatus) -> OrderModel:
        """
        Atomically update the status of an Order and log the change.
        Uses a row-level lock to ensure concurrency safety.
        Raises NotFoundError if the Order is not found.
        """
        order = (
            self.db.query(OrderModel)
            .filter(OrderModel.id == order_id)
            .with_for_update()
            .one_or_none()
        )
        if not order:
            raise NotFoundError("Order", order_id)
        order.status = new_status
        history_entry = OrderStatusHistoryModel(
            status=new_status,
            timestamp=datetime.now(timezone.utc),
        )
        order.status_history.append(history_entry)
        self.db.commit()
        self.db.refresh(order)
        return cast(OrderModel, order)
