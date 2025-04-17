import uuid
from datetime import datetime, timedelta
from typing import List

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from huuva_backend.core.entities.item import ItemCreate
from huuva_backend.core.entities.item import ItemStatus as ItemStatusEnum
from huuva_backend.core.entities.order import (
    Customer,
    DeliveryAddress,
    OrderCreate,
    OrderStatusHistory,
)
from huuva_backend.core.entities.order_status import OrderStatus as OrderStatusEnum
from huuva_backend.db.models.order import Order as OrderModel
from huuva_backend.db.repositories.item import ItemRepository
from huuva_backend.db.repositories.order import OrderRepository


# Base fixed timestamp for deterministic fixtures
@pytest.fixture(scope="session")
def base_time() -> datetime:
    """Base timestamp for tests."""
    return datetime(2025, 4, 17, 12, 0, 0)


@pytest.fixture
def order_repo(dbsession: AsyncSession) -> OrderRepository:
    """Order repository fixture."""
    return OrderRepository(dbsession)


@pytest.fixture
def item_repo(dbsession: AsyncSession) -> ItemRepository:
    """Item repository fixture."""
    return ItemRepository(dbsession)


@pytest.fixture
def order_id() -> uuid.UUID:
    """Order ID fixture."""
    return uuid.UUID("12345678-1234-5678-1234-567812345678")


@pytest.fixture
def brand_id() -> uuid.UUID:
    """Brand ID fixture."""
    return uuid.UUID("87654321-4321-8765-4321-876543210000")


@pytest.fixture
def account_id() -> uuid.UUID:
    """Account ID fixture."""
    return uuid.UUID("11111111-2222-3333-4444-555555555555")


@pytest.fixture
def pickup_time(base_time: datetime) -> datetime:
    """Pickup time fixture."""
    return base_time + timedelta(hours=1)


@pytest.fixture
def item_creates() -> List[ItemCreate]:
    """Item creation data fixture."""
    return [
        ItemCreate(
            plu="ITEM001",
            name="Burger",
            quantity=2,
            status=ItemStatusEnum.ORDERED,
        ),
        ItemCreate(
            plu="ITEM002",
            name="Fries",
            quantity=1,
            status=ItemStatusEnum.ORDERED,
        ),
    ]


@pytest.fixture
def status_history(base_time: datetime) -> List[OrderStatusHistory]:
    """Order status history fixture."""
    return [
        OrderStatusHistory(
            status=OrderStatusEnum.RECEIVED,
            timestamp=base_time - timedelta(minutes=10),
        ),
    ]


@pytest.fixture
def customer() -> Customer:
    """Customer fixture."""
    return Customer(name="John Doe", phone_number="+1234567890")


@pytest.fixture
def delivery_address() -> DeliveryAddress:
    """Delivery address fixture."""
    return DeliveryAddress(city="Test City", street="123 Test St", postal_code="12345")


@pytest.fixture
def order_create_data(
    order_id: uuid.UUID,
    brand_id: uuid.UUID,
    account_id: uuid.UUID,
    pickup_time: datetime,
    item_creates: List[ItemCreate],
    status_history: List[OrderStatusHistory],
    customer: Customer,
    delivery_address: DeliveryAddress,
) -> OrderCreate:
    """Order creation data fixture."""
    return OrderCreate(
        id=order_id,
        brand_id=brand_id,
        account=account_id,
        channel_order_id="ORDER_123",
        customer=customer,
        delivery_address=delivery_address,
        pickup_time=pickup_time,
        status=OrderStatusEnum.RECEIVED,
        items=item_creates,
        status_history=status_history,
    )


@pytest.fixture
async def existing_order(
    order_create_data: OrderCreate,
    order_repo: OrderRepository,
) -> OrderModel:
    """Fixture for an existing order."""
    return await order_repo.create(order_create_data)


@pytest.fixture
async def second_order(
    brand_id: uuid.UUID,
    account_id: uuid.UUID,
    pickup_time: datetime,
    item_creates: List[ItemCreate],
    base_time: datetime,
    customer: Customer,
    delivery_address: DeliveryAddress,
    order_repo: OrderRepository,
) -> OrderModel:
    """Fixture for a second order."""
    oc = OrderCreate(
        id=uuid.uuid4(),
        brand_id=brand_id,
        account=account_id,
        channel_order_id="ORDER_456",
        customer=customer,
        delivery_address=delivery_address,
        pickup_time=pickup_time,
        status=OrderStatusEnum.PREPARING,
        items=item_creates,
        status_history=[
            OrderStatusHistory(
                status=OrderStatusEnum.PREPARING,
                timestamp=base_time - timedelta(minutes=5),
            ),
        ],
    )
    return await order_repo.create(oc)


@pytest.fixture
async def different_account_order(
    brand_id: uuid.UUID,
    pickup_time: datetime,
    item_creates: List[ItemCreate],
    base_time: datetime,
    customer: Customer,
    delivery_address: DeliveryAddress,
    order_repo: OrderRepository,
) -> OrderModel:
    """Fixture for an order with a different account ID."""
    different_account_id = uuid.uuid4()
    oc = OrderCreate(
        id=uuid.uuid4(),
        brand_id=brand_id,
        account=different_account_id,
        channel_order_id="ORDER_789",
        customer=customer,
        delivery_address=delivery_address,
        pickup_time=pickup_time,
        status=OrderStatusEnum.RECEIVED,
        items=item_creates,
        status_history=[
            OrderStatusHistory(
                status=OrderStatusEnum.RECEIVED,
                timestamp=base_time - timedelta(minutes=15),
            ),
        ],
    )
    return await order_repo.create(oc)
