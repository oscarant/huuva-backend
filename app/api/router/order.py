from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db

router = APIRouter(prefix="/orders", tags=["orders"])

# TODO: Make service for bussiness logic


@router.post("/", response_model=None, status_code=status.HTTP_201_CREATED)
def create_order() -> None:
    """
    Create a new order and its associated items and status history.
    """


@router.get("/{order_id}", response_model=None)
def get_order(order_id: str, db: Session = Depends(get_db)) -> None:
    """
    Retrieve an order based on its unique UUID.
    """


@router.patch("/{order_id}/status", response_model=None)
def update_order_status() -> None:
    """
    Update the status of an entire order.
    A corresponding entry is added to the status history.
    """


@router.patch("/{order_id}/items/{plu}/status", response_model=None)
def update_item_status() -> None:
    """
    Update the status of an individual order item identified by its PLU.
    A corresponding entry is added to the status history.
    """
