from datetime import datetime, timezone
from typing import Optional, cast

from sqlalchemy.orm import Session

from app.models.order import Item as ItemModel
from app.models.order import (
    ItemStatus,
)
from app.models.order import ItemStatusHistory as ItemStatusHistoryModel
from app.models.order import Order as OrderModel
from app.models.order import (
    OrderStatus,
)
from app.models.order import OrderStatusHistory as OrderStatusHistoryModel
from app.schemas.order import OrderCreate


def create_order(db: Session, order_in: OrderCreate) -> OrderModel:
    """
    Create a new Order (and associated items/status history) in the database.

    Assumptions:
      - The account field uniquely identifies a customer.
    """
    order = OrderModel(
        account=order_in.account,
        brand_id=order_in.brand_id,
        channel_order_id=order_in.channel_order_id,
        customer_name=order_in.customer_name,
        customer_phone=order_in.customer_phone,
        pickup_time=order_in.pickup_time,
        status=order_in.status,  # assuming the enum value is directly provided
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
                status=hist_in.status, timestamp=hist_in.timestamp
            )
            order.status_history.append(history_entry)

    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_order(db: Session, order_id: str) -> Optional[OrderModel]:
    """
    Retrieve an order by its UUID.
    """
    result = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    return cast(Optional[OrderModel], result)


def update_order_status(
    db: Session, order: OrderModel, new_status: OrderStatus
) -> OrderModel:
    """
    Update the overall status of an order and log the change.
    """
    order.status = new_status
    history_entry = OrderStatusHistoryModel(
        status=new_status, timestamp=datetime.now(timezone.utc)
    )
    order.status_history.append(history_entry)
    db.commit()
    db.refresh(order)
    return order


def update_item_status(
    db: Session, item: ItemModel, new_status: ItemStatus
) -> ItemModel:
    """
    Update the status of a specific order item and log the change.
    """
    item.status = new_status
    history_entry = ItemStatusHistoryModel(
        status=new_status, timestamp=datetime.now(timezone.utc)
    )
    item.status_history.append(history_entry)
    db.commit()
    db.refresh(item)
    return item
