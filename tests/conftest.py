"""
Shared pytest fixtures for repository and service layer tests.

Also includes FastAPI app and HTTP client setup.
Includes: OrderRepository, ItemRepository, OrderService, ItemService,
and common data fixtures.
"""

from datetime import datetime, timedelta
from typing import Any, AsyncGenerator, List
from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from huuva_backend.core.entities.item import ItemCreate
from huuva_backend.core.entities.item import ItemStatus as ItemStatusEnum
from huuva_backend.core.entities.order import (
    Customer,
    DeliveryAddress,
    OrderCreate,
    OrderStatusHistory,
)
from huuva_backend.core.entities.order_status import OrderStatus as OrderStatusEnum
from huuva_backend.db.database import get_db_session
from huuva_backend.db.models.order import Order as OrderModel
from huuva_backend.db.repositories.item import ItemRepository
from huuva_backend.db.repositories.order import OrderRepository
from huuva_backend.db.utils import create_database, drop_database
from huuva_backend.services.item import ItemService
from huuva_backend.services.order import OrderService
from huuva_backend.settings import settings
from huuva_backend.web.application import get_app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """
    Backend for anyio pytest plugin.

    :return: backend name.
    """
    return "asyncio"


@pytest.fixture(scope="session")
async def _engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Create engine and databases.

    :yield: new engine.
    """
    from huuva_backend.db.meta import meta
    from huuva_backend.db.models import load_all_models

    load_all_models()

    await create_database()

    engine = create_async_engine(str(settings.db_url))
    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)

    try:
        yield engine
    finally:
        await engine.dispose()
        await drop_database()


@pytest.fixture
async def dbsession(
    _engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Get session to database.

    Fixture that returns a SQLAlchemy session with a SAVEPOINT, and the rollback to it
    after the test completes.

    :param _engine: current engine.
    :yields: async session.
    """
    connection = await _engine.connect()
    trans = await connection.begin()

    session_maker = async_sessionmaker(
        connection,
        expire_on_commit=False,
    )
    session = session_maker()

    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await connection.close()


@pytest.fixture
def fastapi_app(
    dbsession: AsyncSession,
) -> FastAPI:
    """
    Fixture for creating FastAPI app.

    :return: fastapi app with mocked dependencies.
    """
    application = get_app()
    application.dependency_overrides[get_db_session] = lambda: dbsession  # type: ignore
    return application


@pytest.fixture
async def client(
    fastapi_app: FastAPI,
    anyio_backend: Any,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture that creates client for requesting server.

    :param fastapi_app: the application.
    :yield: client for the app.
    """
    async with AsyncClient(app=fastapi_app, base_url="http://test", timeout=2.0) as ac:
        yield ac


@pytest.fixture(scope="session")
def base_time() -> datetime:
    """Return a fixed datetime for deterministic tests."""
    return datetime(2025, 4, 17, 12, 0, 0)


@pytest.fixture
def order_repo(dbsession: AsyncSession) -> OrderRepository:
    """Provide an OrderRepository using the AsyncSession."""
    return OrderRepository(dbsession)


@pytest.fixture
def item_repo(dbsession: AsyncSession) -> ItemRepository:
    """Provide an ItemRepository using the AsyncSession."""
    return ItemRepository(dbsession)


@pytest.fixture
def order_service(
    order_repo: OrderRepository,
    item_repo: ItemRepository,
) -> OrderService:
    """Instantiate the OrderService with its repository."""
    return OrderService(order_repository=order_repo, item_repository=item_repo)


@pytest.fixture
def item_service(item_repo: ItemRepository) -> ItemService:
    """Instantiate the ItemService with its repository."""
    return ItemService(item_repository=item_repo)


@pytest.fixture
def order_id() -> str:
    """Fixed UUID for testing order IDs."""
    return str("12345678-1234-5678-1234-567812345678")


@pytest.fixture
def brand_id() -> str:
    """Fixed UUID for testing brand IDs."""
    return str("87654321-4321-8765-4321-876543210000")


@pytest.fixture
def account_id() -> str:
    """Fixed UUID for testing account IDs."""
    return str("11111111-2222-3333-4444-555555555555")


@pytest.fixture
def pickup_time(base_time: datetime) -> datetime:
    """Return a pickup_time one hour after the base_time."""
    return base_time + timedelta(hours=1)


@pytest.fixture
def item_creates() -> List[ItemCreate]:
    """List of ItemCreate entities for seeding orders."""
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
    """Initial OrderStatusHistory entries for seeding orders."""
    return [
        OrderStatusHistory(
            status=OrderStatusEnum.RECEIVED,
            timestamp=base_time - timedelta(minutes=10),
        ),
    ]


@pytest.fixture
def customer() -> Customer:
    """Customer entity for seeding orders."""
    return Customer(name="John Doe", phone_number="+1234567890")


@pytest.fixture
def delivery_address() -> DeliveryAddress:
    """DeliveryAddress for seeding orders."""
    return DeliveryAddress(city="Test City", street="123 Test St", postal_code="12345")


@pytest.fixture
def order_create_data(
    order_id: str,
    brand_id: str,
    account_id: str,
    pickup_time: datetime,
    item_creates: List[ItemCreate],
    status_history: List[OrderStatusHistory],
    customer: Customer,
    delivery_address: DeliveryAddress,
) -> OrderCreate:
    """Construct an OrderCreate object for tests."""
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
    """Create and return an existing OrderModel for tests."""
    return await order_repo.create(order_create_data)


@pytest.fixture
async def second_order(
    brand_id: str,
    account_id: str,
    pickup_time: datetime,
    item_creates: List[ItemCreate],
    base_time: datetime,
    customer: Customer,
    delivery_address: DeliveryAddress,
    order_repo: OrderRepository,
) -> OrderModel:
    """Create and return a second OrderModel for tests."""
    oc = OrderCreate(
        id=str(uuid4()),
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
    brand_id: str,
    pickup_time: datetime,
    item_creates: List[ItemCreate],
    base_time: datetime,
    customer: Customer,
    delivery_address: DeliveryAddress,
    order_repo: OrderRepository,
) -> OrderModel:
    """Create and return an OrderModel with a different account."""
    different_account_id = str(uuid4())
    oc = OrderCreate(
        id=str(uuid4()),
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


@pytest.fixture
async def first_item_plu(existing_order: OrderModel) -> str:
    """Return the PLU of the first item in the existing order."""
    return existing_order.items[0].plu
