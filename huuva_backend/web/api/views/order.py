from typing import List

from fastapi import APIRouter, Depends, status

from huuva_backend.core.entities.item import ItemUpdate as CoreItemUpdate
from huuva_backend.core.entities.order import OrderCreate as CoreOrderCreate
from huuva_backend.core.entities.order import OrderUpdate as CoreOrderUpdate
from huuva_backend.core.entities.order_status import OrderStatus as CoreOrderStatus
from huuva_backend.dependencies import (
    get_item_service,
    get_item_update_entity,
    get_order_create_entity,
    get_order_service,
    get_order_update_entity,
)
from huuva_backend.services.item import ItemService
from huuva_backend.services.order import OrderService
from huuva_backend.web.api.api_formats.item import Item as ApiItem
from huuva_backend.web.api.api_formats.order import (
    Order as ApiOrder,
)
from huuva_backend.web.api.api_formats.order import (
    OrderQueryParams,
)

router = APIRouter()


@router.get("/", response_model=List[ApiOrder])
async def list_orders(
    query_params: OrderQueryParams = Depends(),
    order_service: OrderService = Depends(get_order_service),
) -> List[ApiOrder]:
    """
    List and filter orders based on criteria.

    Query parameters:
    - status: Filter by order status value (as integer)
    - account: Filter by account UUID
    - from:   Filter orders created after this date
    - to:     Filter orders created before this date
    """
    cores = await order_service.list_orders(
        status=(
            CoreOrderStatus(query_params.status.value) if query_params.status else None
        ),
        account=query_params.account,
        from_date=query_params.from_date,
        to_date=query_params.to_date,
    )
    # Dump core and re-validate into ApiOrder so that the response_model
    # sees the right camelCase fields and enum names.
    return [ApiOrder.model_validate(c.model_dump()) for c in cores]


@router.post("/", response_model=ApiOrder, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: CoreOrderCreate = Depends(get_order_create_entity),
    order_service: OrderService = Depends(get_order_service),
) -> ApiOrder:
    """Create a new order and its associated items and status history."""
    core = await order_service.create_order(order_in)
    return ApiOrder.model_validate(core.model_dump())


@router.get("/{order_id}", response_model=ApiOrder)
async def get_order(
    order_id: str,
    order_service: OrderService = Depends(get_order_service),
) -> ApiOrder:
    """Retrieve an order by its ID."""
    core = await order_service.get_order(order_id)
    return ApiOrder.model_validate(core.model_dump())


@router.patch("/{order_id}", response_model=ApiOrder)
async def update_order_status(
    order_id: str,
    order_up: CoreOrderUpdate = Depends(get_order_update_entity),
    order_service: OrderService = Depends(get_order_service),
) -> ApiOrder:
    """
    Update the status of an entire order.

    A corresponding entry is added to the status history.
    """
    core = await order_service.update_order(order_id, order_up)
    return ApiOrder.model_validate(core.model_dump())


@router.patch("/{order_id}/items/{plu}", response_model=ApiItem)
async def update_item_status(
    order_id: str,
    plu: str,
    item_up: CoreItemUpdate = Depends(get_item_update_entity),
    item_service: ItemService = Depends(get_item_service),
) -> ApiItem:
    """Update the status of an individual order item and log the change."""
    core = await item_service.update(order_id, plu, item_up)
    return ApiItem.model_validate(core.model_dump())
