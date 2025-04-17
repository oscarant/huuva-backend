from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from huuva_backend.core.entities.order import (
    OrderCreate,
    OrderUpdate,
)
from huuva_backend.core.entities.order_status import OrderStatus as OrderStatusEnum
from huuva_backend.db.models.order import Order as OrderModel
from huuva_backend.db.models.order_status import OrderStatus as OrderStatusModel
from huuva_backend.db.repositories.order import OrderRepository
from huuva_backend.exceptions.exceptions import ConflictError, NotFoundError


class TestOrderRepository:
    @pytest.mark.anyio
    async def test_create_order_success(
        self,
        order_create_data: OrderCreate,
        order_repo: OrderRepository,
    ) -> None:
        """Test creating an order successfully."""
        # Arrange
        # Act
        order = await order_repo.create(order_create_data)

        # Assert
        assert order is not None
        assert order.id == order_create_data.id
        assert order.account == order_create_data.account
        assert order.brand_id == order_create_data.brand_id
        assert order.channel_order_id == order_create_data.channel_order_id
        assert order.customer_name == order_create_data.customer.name
        assert order.customer_phone == order_create_data.customer.phone_number
        assert order.pickup_time == order_create_data.pickup_time
        assert order.status.value == order_create_data.status.value
        assert order.delivery_city == order_create_data.delivery_address.city
        assert order.delivery_street == order_create_data.delivery_address.street
        assert (
            order.delivery_postal_code == order_create_data.delivery_address.postal_code
        )

        assert len(order.items) == len(order_create_data.items)
        for i, item in enumerate(order.items):
            assert item.plu == order_create_data.items[i].plu
            assert item.name == order_create_data.items[i].name
            assert item.quantity == order_create_data.items[i].quantity

        # Verify status history was created
        assert len(order.status_history) == len(order_create_data.status_history)
        for i, history in enumerate(order.status_history):
            assert (
                history.status.value == order_create_data.status_history[i].status.value
            )

    @pytest.mark.anyio
    async def test_create_duplicate_order(
        self,
        existing_order: OrderModel,
        order_create_data: OrderCreate,
        order_repo: OrderRepository,
    ) -> None:
        """Test that creating an order with the same ID raises ConflictError."""
        # Act & Assert
        with pytest.raises(ConflictError) as exc_info:
            await order_repo.create(order_create_data)

        assert str(order_create_data.id) in str(exc_info.value)

    @pytest.mark.anyio
    async def test_get_order_success(
        self,
        existing_order: OrderModel,
        order_repo: OrderRepository,
    ) -> None:
        """Test getting an existing order successfully."""
        # Act
        order = await order_repo.get(existing_order.id)

        # Assert
        assert order is not None
        assert order.id == existing_order.id
        assert order.account == existing_order.account
        assert order.brand_id == existing_order.brand_id

    @pytest.mark.anyio
    async def test_get_nonexistent_order(
        self,
        order_repo: OrderRepository,
    ) -> None:
        """Test that getting a non-existent order raises NotFoundError."""
        # Arrange
        non_existent_id = str(uuid4())

        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            await order_repo.get(non_existent_id)

        assert str(non_existent_id) in str(exc_info.value)

    @pytest.mark.anyio
    async def test_update_order_status(
        self,
        existing_order: OrderModel,
        order_repo: OrderRepository,
    ) -> None:
        """Test updating an order's status."""
        # Arrange
        new_status = OrderStatusEnum.PREPARING
        order_update = OrderUpdate(status=new_status)
        before_count = len(existing_order.status_history)
        # Act
        updated_order = await order_repo.update(existing_order.id, order_update)

        # Assert
        assert updated_order is not None
        assert updated_order.status.value == new_status.value

        # Verify status history was updated
        # Find the new history entry (it should be the latest one)
        newest_history = max(updated_order.status_history, key=lambda h: h.timestamp)
        assert newest_history.status.value == new_status.value

        # Verify the previous status is still in the history
        assert len(updated_order.status_history) == before_count + 1

    @pytest.mark.anyio
    async def test_update_nonexistent_order(
        self,
        order_repo: OrderRepository,
    ) -> None:
        """Test that updating a non-existent order raises NotFoundError."""
        # Arrange
        non_existent_id = str(uuid4())
        order_update = OrderUpdate(status=OrderStatusEnum.PREPARING)

        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            await order_repo.update(non_existent_id, order_update)

        assert str(non_existent_id) in str(exc_info.value)

    @pytest.mark.anyio
    async def test_list_orders_no_filters(
        self,
        existing_order: OrderModel,
        second_order: OrderModel,
        different_account_order: OrderModel,
        order_repo: OrderRepository,
    ) -> None:
        """Test listing orders without any filters."""
        # Act
        orders = await order_repo.list()

        # Assert
        assert isinstance(orders, list)
        assert len(orders) >= 3
        order_ids = {order.id for order in orders}
        assert existing_order.id in order_ids
        assert second_order.id in order_ids
        assert different_account_order.id in order_ids

    @pytest.mark.anyio
    async def test_list_orders_by_status(
        self,
        existing_order: OrderModel,
        second_order: OrderModel,
        order_repo: OrderRepository,
    ) -> None:
        """Test listing orders filtered by status."""
        # Act - Get RECEIVED orders
        received_orders = await order_repo.list(status=OrderStatusModel.RECEIVED)

        # Assert
        assert all(
            order.status == OrderStatusModel.RECEIVED for order in received_orders
        )
        assert existing_order.id in {order.id for order in received_orders}
        assert second_order.id not in {order.id for order in received_orders}

        # Act - Get PREPARING orders
        preparing_orders = await order_repo.list(status=OrderStatusModel.PREPARING)

        # Assert
        assert all(
            order.status == OrderStatusModel.PREPARING for order in preparing_orders
        )
        assert second_order.id in {order.id for order in preparing_orders}
        assert existing_order.id not in {order.id for order in preparing_orders}

    @pytest.mark.anyio
    async def test_list_orders_by_account(
        self,
        existing_order: OrderModel,
        second_order: OrderModel,
        different_account_order: OrderModel,
        account_id: str,
        order_repo: OrderRepository,
    ) -> None:
        """Test listing orders filtered by account."""
        # Act
        account_orders = await order_repo.list(account=account_id)
        different_account_orders = await order_repo.list(
            account=different_account_order.account,
        )

        # Assert
        assert len(account_orders) >= 2
        assert all(order.account == account_id for order in account_orders)
        assert existing_order.id in {order.id for order in account_orders}
        assert second_order.id in {order.id for order in account_orders}
        assert different_account_order.id not in {order.id for order in account_orders}

        assert len(different_account_orders) >= 1
        assert all(
            order.account == different_account_order.account
            for order in different_account_orders
        )
        assert different_account_order.id in {
            order.id for order in different_account_orders
        }
        assert existing_order.id not in {order.id for order in different_account_orders}

    @pytest.mark.anyio
    async def test_list_orders_by_date_range(
        self,
        existing_order: OrderModel,
        order_repo: OrderRepository,
    ) -> None:
        """Test listing orders filtered by date range."""
        # Arrange
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)
        future = now + timedelta(days=7)

        # Act - Orders within valid date range
        orders_in_range = await order_repo.list(from_date=yesterday, to_date=tomorrow)

        # Assert
        assert len(orders_in_range) >= 1
        assert existing_order.id in {order.id for order in orders_in_range}

        # Act - Orders in future date range (should be empty)
        future_orders = await order_repo.list(from_date=tomorrow, to_date=future)

        # Assert
        assert all(order.id != existing_order.id for order in future_orders)

    @pytest.mark.anyio
    async def test_list_orders_with_multiple_filters(
        self,
        existing_order: OrderModel,
        second_order: OrderModel,
        different_account_order: OrderModel,
        account_id: str,
        order_repo: OrderRepository,
    ) -> None:
        """Test listing orders with multiple filters applied."""
        # Arrange
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)

        # Act - Filter by account and status
        filtered_orders = await order_repo.list(
            account=account_id,
            status=OrderStatusModel.RECEIVED,
        )

        # Assert
        assert all(order.account == account_id for order in filtered_orders)
        assert all(
            order.status == OrderStatusModel.RECEIVED for order in filtered_orders
        )
        assert existing_order.id in {order.id for order in filtered_orders}
        assert second_order.id not in {order.id for order in filtered_orders}

        # Act - Filter by account, status, and date range
        date_filtered_orders = await order_repo.list(
            account=account_id,
            status=OrderStatusModel.RECEIVED,
            from_date=yesterday,
            to_date=tomorrow,
        )

        # Assert
        assert all(order.account == account_id for order in date_filtered_orders)
        assert all(
            order.status == OrderStatusModel.RECEIVED for order in date_filtered_orders
        )
        assert all(
            yesterday <= order.created_at <= tomorrow for order in date_filtered_orders
        )
        assert existing_order.id in {order.id for order in date_filtered_orders}
