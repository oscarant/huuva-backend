from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.repositories.item import ItemRepository
from app.db.repositories.order import OrderRepository
from app.services.item import ItemService
from app.services.order import OrderService


def get_order_service(db: AsyncSession = Depends(get_db)) -> OrderService:
    repo = OrderRepository(db=db)
    return OrderService(order_repository=repo)


def get_item_service(db: AsyncSession = Depends(get_db)) -> ItemService:
    repo = ItemRepository(db=db)
    return ItemService(item_repository=repo)
