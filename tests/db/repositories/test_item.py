import uuid

import pytest

from huuva_backend.core.entities.item import ItemStatus as ItemStatusEnum
from huuva_backend.core.entities.item import ItemUpdate
from huuva_backend.db.models.item import Item as ItemModel
from huuva_backend.db.models.order import Order as OrderModel
from huuva_backend.db.repositories.item import ItemRepository
from huuva_backend.exceptions.exceptions import NotFoundError


@pytest.fixture
async def existing_item(
    item_repo: ItemRepository,
    existing_order: OrderModel,
) -> ItemModel:
    """Fixture to create an item in the database."""
    # pick the first item from the seeded order
    first_plu = existing_order.items[0].plu
    return await item_repo.get(existing_order.id, first_plu)


class TestItemRepository:
    @pytest.mark.anyio
    async def test_get_item_success(
        self,
        existing_item: ItemModel,
        existing_order: OrderModel,
    ) -> None:
        """Tests that getting an item works as expected."""
        assert existing_item is not None
        assert existing_item.order_id == existing_order.id
        # fields match create data
        assert existing_item.plu in {"ITEM001", "ITEM002"}
        assert existing_item.name in {"Burger", "Fries"}
        assert existing_item.quantity in (1, 2)
        # initial status is ORDERED
        assert existing_item.status.value == ItemStatusEnum.ORDERED.value
        # one history entry seeded
        assert len(existing_item.status_history) == 1
        assert (
            existing_item.status_history[0].status.value == ItemStatusEnum.ORDERED.value
        )

    @pytest.mark.anyio
    async def test_get_item_not_found(self, item_repo: ItemRepository) -> None:
        """Tests that getting a non-existing item raises NotFoundError."""
        fake_order = uuid.uuid4()
        with pytest.raises(NotFoundError):
            await item_repo.get(fake_order, "NO_SUCH_ITEM")

    @pytest.mark.anyio
    async def test_update_item_status_success(
        self,
        item_repo: ItemRepository,
        existing_item: ItemModel,
    ) -> None:
        """Tests that updating an item's status works as expected."""
        original_history_count = len(existing_item.status_history)
        new_status = ItemStatusEnum.PREPARING
        update = ItemUpdate(status=new_status)

        updated = await item_repo.update(
            existing_item.order_id,
            existing_item.plu,
            update,
        )
        # status updated
        assert updated.status.value == new_status.value
        # history length incremented
        assert len(updated.status_history) == original_history_count + 1
        # newest entry matches new status
        newest = max(updated.status_history, key=lambda h: h.timestamp)
        assert newest.status.value == new_status.value
        # previous entry still present
        assert any(
            h.status.value == ItemStatusEnum.ORDERED.value
            for h in updated.status_history
        )

    @pytest.mark.anyio
    async def test_update_item_not_found(self, item_repo: ItemRepository) -> None:
        """Tests that updating a non-existing item raises NotFoundError."""
        fake_order = uuid.uuid4()
        with pytest.raises(NotFoundError):
            await item_repo.update(
                fake_order,
                "NO_ITEM",
                ItemUpdate(status=ItemStatusEnum.READY),
            )
