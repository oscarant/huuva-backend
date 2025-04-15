from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from huuva_backend.db.database import get_db
from huuva_backend.db.repositories.item import ItemRepository
from huuva_backend.db.repositories.order import OrderRepository
from huuva_backend.services.item import ItemService
from huuva_backend.services.order import OrderService


def get_order_service(db: AsyncSession = Depends(get_db)) -> OrderService:
    """Dependency to get the OrderService instance."""
    repo = OrderRepository(db=db)
    return OrderService(order_repository=repo)


def get_item_service(db: AsyncSession = Depends(get_db)) -> ItemService:
    """Dependency to get the ItemService instance."""
    repo = ItemRepository(db=db)
    return ItemService(item_repository=repo)
