from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.mappings import map_item_status, map_order_status
from app.repositories import order as order_repo
from app.schemas.order import (
    Item,
    ItemStatusUpdate,
    Order,
    OrderCreate,
    OrderStatusUpdate,
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate, db: Session = Depends(get_db)) -> Order:
    """
    Create a new order and its associated items and status history.
    """
    new_order = order_repo.create_order(db, order)
    return new_order


@router.get("/{order_id}", response_model=Order)
def get_order(order_id: str, db: Session = Depends(get_db)) -> Order:
    """
    Retrieve an order based on its unique UUID.
    """
    order_obj = order_repo.get_order(db, order_id)
    if not order_obj:
        raise HTTPException(status_code=404, detail="Order not found")
    return order_obj


@router.patch("/{order_id}/status", response_model=Order)
def update_order_status(
    order_id: str, update: OrderStatusUpdate, db: Session = Depends(get_db)
) -> Order:
    """
    Update the status of an entire order.
    A corresponding entry is added to the status history.
    """
    order_obj = order_repo.get_order(db, order_id)
    if not order_obj:
        raise HTTPException(status_code=404, detail="Order not found")
    model_status = map_order_status(update.status)
    updated_order = order_repo.update_order_status(db, order_obj, model_status)
    return updated_order


@router.patch("/{order_id}/items/{plu}/status", response_model=Item)
def update_item_status(
    order_id: str, plu: str, update: ItemStatusUpdate, db: Session = Depends(get_db)
) -> Item:
    """
    Update the status of an individual order item identified by its PLU.
    A corresponding entry is added to the status history.
    """
    item_obj = order_repo.get_item_by_plu(db, order_id, plu)
    if not item_obj:
        raise HTTPException(status_code=404, detail="Item not found")
    model_status = map_item_status(update.status)
    updated_item = order_repo.update_item_status(db, item_obj, model_status)
    return updated_item
