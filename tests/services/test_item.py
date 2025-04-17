"""Test suite for the ItemService."""

import uuid

import pytest

from huuva_backend.core.entities.item import (
    Item as ItemEntity,
)
from huuva_backend.core.entities.item import (
    ItemStatus as ItemStatusEnum,
)
from huuva_backend.core.entities.item import (
    ItemUpdate,
)
from huuva_backend.db.models.order import Order as OrderModel
from huuva_backend.exceptions.exceptions import NotFoundError
from huuva_backend.services.item import ItemService


@pytest.mark.anyio
async def test_get_item_success(
    item_service: ItemService,
    existing_order: OrderModel,
    first_item_plu: str,
) -> None:
    """Test that ItemService.get returns the correct ItemEntity."""
    item = await item_service.get(existing_order.id, first_item_plu)
    assert isinstance(item, ItemEntity)
    assert item.plu == first_item_plu
    assert item.name in ("Burger", "Fries")
    assert item.quantity > 0
    assert item.status == ItemStatusEnum.ORDERED
    assert len(item.status_history) == 1
    assert item.status_history[0].status == ItemStatusEnum.ORDERED


@pytest.mark.anyio
async def test_get_item_not_found(item_service: ItemService) -> None:
    """Test that ItemService.get raises NotFoundError for missing items."""
    with pytest.raises(NotFoundError):
        await item_service.get(uuid.uuid4(), "NONEXISTENT")


@pytest.mark.anyio
async def test_update_item_status_success(
    item_service: ItemService,
    existing_order: OrderModel,
    first_item_plu: str,
) -> None:
    """Test that ItemService.update correctly updates status and history."""
    before = await item_service.get(existing_order.id, first_item_plu)
    original_count = len(before.status_history)
    update = ItemUpdate(status=ItemStatusEnum.PREPARING)

    updated = await item_service.update(existing_order.id, first_item_plu, update)
    assert updated.status == ItemStatusEnum.PREPARING
    assert len(updated.status_history) == original_count + 1
    assert updated.status_history[-1].status == ItemStatusEnum.PREPARING
    assert any(h.status == ItemStatusEnum.ORDERED for h in updated.status_history)


@pytest.mark.anyio
async def test_update_item_not_found(item_service: ItemService) -> None:
    """Test that ItemService.update raises NotFoundError for missing items."""
    with pytest.raises(NotFoundError):
        await item_service.update(
            uuid.uuid4(),
            "NO_SUCH_PLU",
            ItemUpdate(status=ItemStatusEnum.READY),
        )
