from fastapi import Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from huuva_backend.core.entities.item import (
    ItemUpdate as CoreItemUpdate,
)
from huuva_backend.core.entities.order import (
    OrderCreate as CoreOrderCreate,
)
from huuva_backend.core.entities.order import (
    OrderUpdate as CoreOrderUpdate,
)
from huuva_backend.db.database import get_db_session
from huuva_backend.db.repositories.item import ItemRepository
from huuva_backend.db.repositories.order import OrderRepository
from huuva_backend.services.item import ItemService
from huuva_backend.services.order import OrderService
from huuva_backend.web.api.api_formats.item import (
    ItemUpdate as ApiItemUpdate,
)
from huuva_backend.web.api.api_formats.order import (
    OrderCreate as ApiOrderCreate,
)
from huuva_backend.web.api.api_formats.order import (
    OrderUpdate as ApiOrderUpdate,
)


def get_order_create_entity(order_in: ApiOrderCreate = Body(...)) -> CoreOrderCreate:
    """
    Transform `ApiOrderCreate` to `CoreOrderCreate`.

    Dependency that:
      1) Parses the request body as `ApiOrderCreate` (camelCase).
      2) Dumps it to a snake_case dict.
      3) Validates that dict into the core `CoreOrderCreate`.
    """
    data = order_in.model_dump()  # camelCase → snake_case
    return CoreOrderCreate.model_validate(data)


def get_order_update_entity(order_up: ApiOrderUpdate = Body(...)) -> CoreOrderUpdate:
    """
    Transform `ApiOrderUpdate` to `CoreOrderUpdate`.

    Dependency that:
      1) Parses the request body as `ApiOrderUpdate` (camelCase).
      2) Dumps it to a snake_case dict.
      3) Validates that dict into the core `CoreOrderUpdate`.
    """
    data = order_up.model_dump()
    return CoreOrderUpdate.model_validate(data)


def get_item_update_entity(item_up: ApiItemUpdate = Body(...)) -> CoreItemUpdate:
    """
    Transform `ApiItemUpdate` to `CoreItemUpdate`.

    Dependency that:
      1) Parses the request body as `ApiItemUpdate` (camelCase).
      2) Dumps it to a snake_case dict.
      3) Validates that dict into the core `CoreItemUpdate`.
    """
    data = item_up.model_dump()
    return CoreItemUpdate.model_validate(data)


def get_order_service(db: AsyncSession = Depends(get_db_session)) -> OrderService:
    """Dependency to get the OrderService instance."""
    repo = OrderRepository(db=db)
    return OrderService(order_repository=repo)


def get_item_service(db: AsyncSession = Depends(get_db_session)) -> ItemService:
    """Dependency to get the ItemService instance."""
    repo = ItemRepository(db=db)
    return ItemService(item_repository=repo)
