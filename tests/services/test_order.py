"""Test suite for the OrderService."""

from uuid import uuid4

import pytest

from huuva_backend.core.entities.order import Order as OrderEntity
from huuva_backend.core.entities.order import OrderCreate, OrderUpdate
from huuva_backend.core.entities.order_status import OrderStatus as OrderStatusEnum
from huuva_backend.db.models.order import Order as OrderModel
from huuva_backend.exceptions.exceptions import NotFoundError
from huuva_backend.services.order import OrderService


@pytest.mark.anyio
async def test_create_order(
    order_service: OrderService,
    order_create_data: OrderCreate,
) -> None:
    """Test that OrderService.create_order returns a valid OrderEntity."""
    order = await order_service.create_order(order_create_data)
    assert isinstance(order, OrderEntity)
    assert order.id == order_create_data.id
    assert order.account == order_create_data.account
    assert order.brand_id == order_create_data.brand_id
    assert order.channel_order_id == order_create_data.channel_order_id
    assert len(order.items) == len(order_create_data.items)
    assert len(order.status_history) == len(order_create_data.status_history)


@pytest.mark.anyio
async def test_get_order_success(
    order_service: OrderService,
    existing_order: OrderModel,
) -> None:
    """Test that OrderService.get_order returns the correct OrderEntity."""
    order = await order_service.get_order(existing_order.id)
    assert isinstance(order, OrderEntity)
    assert order.id == existing_order.id
    assert order.account == existing_order.account


@pytest.mark.anyio
async def test_get_order_not_found(order_service: OrderService) -> None:
    """Test that OrderService.get_order raises NotFoundError for missing orders."""
    with pytest.raises(NotFoundError):
        await order_service.get_order(str(uuid4()))


@pytest.mark.anyio
async def test_list_orders(
    order_service: OrderService,
    existing_order: OrderModel,
    second_order: OrderModel,
    different_account_order: OrderModel,
) -> None:
    """Test that OrderService.list_orders returns all existing orders."""
    orders = await order_service.list_orders()
    ids = {o.id for o in orders}
    assert existing_order.id in ids
    assert second_order.id in ids
    assert different_account_order.id in ids


@pytest.mark.anyio
async def test_update_order_status_success(
    order_service: OrderService,
    existing_order: OrderModel,
) -> None:
    """Test that OrderService.update_order correctly updates status and history."""
    before = await order_service.get_order(existing_order.id)
    original_count = len(before.status_history)
    update = OrderUpdate(status=OrderStatusEnum.PREPARING)

    updated = await order_service.update_order(existing_order.id, update)
    assert updated.status == OrderStatusEnum.PREPARING
    assert len(updated.status_history) == original_count + 1
    assert updated.status_history[-1].status == OrderStatusEnum.PREPARING


@pytest.mark.anyio
async def test_update_order_not_found(order_service: OrderService) -> None:
    """Test that OrderService.update_order raises NotFoundError for missing orders."""
    with pytest.raises(NotFoundError):
        await order_service.update_order(
            str(uuid4()),
            OrderUpdate(status=OrderStatusEnum.READY),
        )
