from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from huuva_backend.db.database import get_db_session
from huuva_backend.services.analytics import AnalyticsService
from huuva_backend.web.api.api_formats.analytics import (
    CustomerOrderCount,
    HourlyThroughput,
    StatusDuration,
)

router = APIRouter()


@router.get("/order-status-durations", response_model=List[StatusDuration])
async def get_order_status_durations(
    db: AsyncSession = Depends(get_db_session),
) -> List[Dict[str, Any]]:
    """Get average time spent in each order status."""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_order_status_durations()


@router.get("/item-status-durations", response_model=List[StatusDuration])
async def get_item_status_durations(
    db: AsyncSession = Depends(get_db_session),
) -> List[Dict[str, Any]]:
    """Get average time spent in each item status."""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_item_status_durations()


@router.get("/hourly-throughput", response_model=List[HourlyThroughput])
async def get_hourly_throughput(
    limit: int = 24,
    db: AsyncSession = Depends(get_db_session),
) -> List[Dict[str, Any]]:
    """Get order throughput per hour."""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_hourly_throughput(limit=limit)


@router.get("/customer-order-counts", response_model=List[CustomerOrderCount])
async def get_customer_order_counts(
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session),
) -> List[Dict[str, Any]]:
    """Get number of orders per customer."""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_customer_order_counts(limit=limit)


# refresh materialized views
@router.get("/refresh-materialized-views", response_model=None)
async def refresh_materialized_views(
    db: AsyncSession = Depends(get_db_session),
) -> None:
    """Refresh materialized views."""
    analytics_service = AnalyticsService(db)
    await analytics_service.refresh_materialized_views()
