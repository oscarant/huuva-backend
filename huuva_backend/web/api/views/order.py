from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status

from huuva_backend.core.entities.item import ItemUpdate as ItemUpdateEntity
from huuva_backend.core.entities.order import OrderCreate as OrderCreateEntity
from huuva_backend.core.entities.order import OrderUpdate as OrderUpdateEntity
from huuva_backend.core.entities.order_status import OrderStatus as OrderStatusEntity
from huuva_backend.dependencies import get_item_service, get_order_service
from huuva_backend.services.item import ItemService
from huuva_backend.services.order import OrderService
from huuva_backend.web.api.api_formats.item import Item, ItemUpdate
from huuva_backend.web.api.api_formats.order import (
    Order,
    OrderCreate,
    OrderQueryParams,
    OrderUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[Order])
async def list_orders(
    query_params: OrderQueryParams = Depends(),
    order_service: OrderService = Depends(get_order_service),
) -> List[Order]:
    """
    List and filter orders based on criteria.

    Query parameters:
    - status: Filter by order status value (as integer)
    - account: Filter by account UUID
    - from: Filter orders created after this date
    - to: Filter orders created before this date
    """
    order_entities = await order_service.list_orders(
        status=(
            OrderStatusEntity(query_params.status.value)
            if query_params.status
            else None
        ),
        account=query_params.account,
        from_date=query_params.from_date,
        to_date=query_params.to_date,
    )
    return [Order.model_validate(order) for order in order_entities]


@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(
    order: OrderCreate,
    order_service: OrderService = Depends(get_order_service),
) -> Order:
    """Create a new order and its associated items and status history."""
    order_entity = await order_service.create_order(
        OrderCreateEntity.model_validate(order),
    )
    return Order.model_validate(order_entity)


@router.get("/{order_id}", response_model=Order)
async def get_order(
    order_id: UUID,
    order_service: OrderService = Depends(get_order_service),
) -> Order:
    """Retrieve an order by its ID."""
    order_entity = await order_service.get_order(order_id)
    return Order.model_validate(order_entity)


@router.patch("/{order_id}", response_model=Order)
async def update_order_status(
    order_id: UUID,
    order_update: OrderUpdate,
    order_service: OrderService = Depends(get_order_service),
) -> Order:
    """
    Update the status of an entire order.

    A corresponding entry is added to the status history.
    """
    order_update_entity = OrderUpdateEntity.model_validate(order_update)
    order_entity = await order_service.update_order(order_id, order_update_entity)
    return Order.model_validate(order_entity)


@router.patch("/{order_id}/items/{plu}", response_model=Item)
async def update_item_status(
    order_id: UUID,
    plu: str,
    item_update: ItemUpdate,
    item_service: ItemService = Depends(get_item_service),
) -> Item:
    """Update the status of an individual order item and log the change."""
    item_update_entity = ItemUpdateEntity.model_validate(item_update)
    item_entity = await item_service.update(order_id, plu, item_update_entity)
    return Item.model_validate(item_entity)
