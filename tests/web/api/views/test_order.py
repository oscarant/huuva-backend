"""
End-to-end tests for the Orders API endpoints.

Builds URLs via FastAPIs url_path_for to ensure correct routing (including any /api
prefix).
"""

import uuid
from datetime import datetime
from typing import List

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from huuva_backend.core.entities.item import ItemCreate
from huuva_backend.core.entities.item_status import ItemStatus as ItemStatusEnum
from huuva_backend.core.entities.order import (
    Customer,
    DeliveryAddress,
)
from huuva_backend.core.entities.order_status import (
    OrderStatus as OrderStatusEnum,
)
from huuva_backend.core.entities.order_status import (
    OrderStatusHistory,
)
from huuva_backend.db.models.order import Order as OrderModel


@pytest.mark.anyio
async def test_list_orders_endpoint(
    fastapi_app: FastAPI,
    client: AsyncClient,
    existing_order: OrderModel,
    second_order: OrderModel,
    different_account_order: OrderModel,
) -> None:
    """GET /orders/ returns all seeded orders."""
    url = fastapi_app.url_path_for("list_orders")
    resp = await client.get(url)
    assert resp.status_code == 200
    data = resp.json()
    returned_ids = {o["id"] for o in data}
    assert str(existing_order.id) in returned_ids
    assert str(second_order.id) in returned_ids
    assert str(different_account_order.id) in returned_ids


@pytest.mark.anyio
async def test_get_order_success(
    fastapi_app: FastAPI,
    client: AsyncClient,
    existing_order: OrderModel,
) -> None:
    """GET /orders/{order_id} for an existing ID returns that order."""
    url = fastapi_app.url_path_for("get_order", order_id=str(existing_order.id))
    resp = await client.get(url)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(existing_order.id)
    assert data["account"] == str(existing_order.account)


@pytest.mark.anyio
async def test_get_order_not_found(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """GET /orders/{order_id} for a non-existent ID returns 404."""
    fake_id = str(uuid.uuid4())
    url = fastapi_app.url_path_for("get_order", order_id=fake_id)
    resp = await client.get(url)
    assert resp.status_code == 404


@pytest.mark.anyio
async def test_create_order_with_fixture_payload(
    fastapi_app: FastAPI,
    client: AsyncClient,
    order_id: uuid.UUID,
    base_time: datetime,
    account_id: uuid.UUID,
    brand_id: uuid.UUID,
    pickup_time: datetime,
    customer: Customer,
    delivery_address: DeliveryAddress,
    item_creates: List[ItemCreate],
    status_history: List[OrderStatusHistory],
) -> None:
    """POST /orders/ with all fields specified should create and return the order."""
    url = fastapi_app.url_path_for("create_order")
    payload = {
        "id": str(order_id),
        "created": base_time.isoformat(),
        "account": str(account_id),
        "brandId": str(brand_id),
        "channelOrderId": "ORDER_FIXTURE",
        "customer": {"name": customer.name, "phoneNumber": customer.phone_number},
        "deliveryAddress": {
            "city": delivery_address.city,
            "street": delivery_address.street,
            "postalCode": delivery_address.postal_code,
        },
        "pickupTime": pickup_time.isoformat(),
        "items": [
            {"plu": item.plu, "name": item.name, "quantity": item.quantity}
            for item in item_creates
        ],
        "status": status_history[0].status.value,
        "statusHistory": [
            {"status": h.status.value, "timestamp": h.timestamp.isoformat()}
            for h in status_history
        ],
    }
    resp = await client.post(url, json=payload)
    assert resp.status_code == 201
    data = resp.json()

    assert data["id"] == payload["id"]
    assert data["account"] == payload["account"]
    assert data["brandId"] == payload["brandId"]
    assert data["channelOrderId"] == payload["channelOrderId"]
    assert data["pickupTime"].startswith(pickup_time.isoformat()[:19])

    returned_plu = [i["plu"] for i in data["items"]]
    expected_plu = [item.plu for item in item_creates]
    assert returned_plu == expected_plu

    assert data["status"] == status_history[0].status.name
    returned_hist = [h["status"] for h in data["statusHistory"]]
    expected_hist = [h.status.name for h in status_history]
    assert returned_hist == expected_hist


@pytest.mark.anyio
async def test_create_order_with_example_payload(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """
    POST /orders/ with the example payload should create and return the mapped order.

    This test is used to verify that the example payload in the documentation is
    correctly mapped to the OrderModel.
    """
    url = fastapi_app.url_path_for("create_order")
    example_payload = {
        "_id": "60f87ea2a52dad8a3fa4860",
        "created": "2021-07-22T20:08:02Z",
        "account": "60bfc6dc4887c9851d5a0246",
        "brandId": "60bfc6dc4887c9851d5a0245",
        "channelOrderId": "TEST1626898082",
        "customer": {"name": "John Doe", "phoneNumber": "+123456789"},
        "deliveryAddress": {
            "city": "Helsinki",
            "street": "Huuvatie 1",
            "postalCode": "00100",
        },
        "pickupTime": "2021-07-22T20:28:02Z",
        "items": [
            {"name": "Hawaii Burger", "plu": "CAT1-0001", "quantity": 1},
            {"name": "Sushi Set Large", "plu": "CAT2-0001", "quantity": 1},
        ],
        "status": 1,
        "statusHistory": [
            {"status": 4, "timestamp": "2021-07-22T20:08:02Z"},
            {"status": 1, "timestamp": "2021-07-22T20:10:00Z"},
        ],
    }
    resp = await client.post(url, json=example_payload)
    assert resp.status_code == 201
    data = resp.json()

    assert data["id"] == example_payload["_id"]
    assert data["channelOrderId"] == example_payload["channelOrderId"]
    assert [i["name"] for i in data["items"]] == [
        "Hawaii Burger",
        "Sushi Set Large",
    ]
    assert data["status"] == OrderStatusEnum.RECEIVED.name
    assert [h["status"] for h in data["statusHistory"]] == [
        OrderStatusEnum.PICKED_UP.name,
        OrderStatusEnum.RECEIVED.name,
    ]


@pytest.mark.anyio
async def test_update_order_status(
    fastapi_app: FastAPI,
    client: AsyncClient,
    existing_order: OrderModel,
) -> None:
    """PATCH /orders/{order_id} updates the order`s status."""
    url = fastapi_app.url_path_for(
        "update_order_status",
        order_id=str(existing_order.id),
    )
    new_status = OrderStatusEnum.PREPARING.value
    resp = await client.patch(url, json={"status": new_status})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == OrderStatusEnum.PREPARING.name


@pytest.mark.anyio
async def test_update_item_status(
    fastapi_app: FastAPI,
    client: AsyncClient,
    existing_order: OrderModel,
    first_item_plu: str,
) -> None:
    """PATCH /orders/{order_id}/items/{plu} updates the items status."""
    url = fastapi_app.url_path_for(
        "update_item_status",
        order_id=str(existing_order.id),
        plu=first_item_plu,
    )
    new_status = ItemStatusEnum.READY.value
    resp = await client.patch(url, json={"status": new_status})
    assert resp.status_code == 200
    data = resp.json()
    assert data["plu"] == first_item_plu
    assert data["status"] == ItemStatusEnum.READY.name
