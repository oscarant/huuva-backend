from typing import Any, Dict, List

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class AnalyticsService:
    """Service for analytics data operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def refresh_materialized_views(self) -> None:
        """Refresh all materialized views for analytics."""
        views = [
            "order_status_duration_avg",
            "item_status_duration_avg",
            "order_hourly_throughput",
            "customer_order_count",
        ]

        for view in views:
            await self.db.execute(text(f"REFRESH MATERIALIZED VIEW {view};"))

        await self.db.commit()

    async def get_order_status_durations(self) -> List[Dict[str, Any]]:
        """Get average time spent in each order status."""
        result = await self.db.execute(
            text(
                """
            SELECT
                status,
                avg_duration_seconds
            FROM order_status_duration_avg
            ORDER BY status;
            """,
            ),
        )
        return [
            {"status": row[0], "avg_duration_seconds": row[1]}
            for row in result.fetchall()
        ]

    async def get_item_status_durations(self) -> List[Dict[str, Any]]:
        """Get average time spent in each item status."""
        result = await self.db.execute(
            text(
                """
            SELECT
                status,
                avg_duration_seconds
            FROM item_status_duration_avg
            ORDER BY status;
            """,
            ),
        )
        return [
            {"status": row[0], "avg_duration_seconds": row[1]}
            for row in result.fetchall()
        ]

    async def get_hourly_throughput(self, limit: int = 24) -> List[Dict[str, Any]]:
        """Get order throughput per hour."""
        result = await self.db.execute(
            text(
                """
            SELECT
                hour,
                order_count
            FROM order_hourly_throughput
            ORDER BY hour DESC
            LIMIT :limit;
            """,
            ),
            {"limit": limit},
        )
        return [{"hour": row[0], "order_count": row[1]} for row in result.fetchall()]

    async def get_customer_order_counts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get number of orders per customer."""
        result = await self.db.execute(
            text(
                """
            SELECT
                account,
                order_count,
                first_order_at,
                last_order_at
            FROM customer_order_count
            ORDER BY order_count DESC
            LIMIT :limit;
            """,
            ),
            {"limit": limit},
        )
        return [
            {
                "account": row[0],
                "order_count": row[1],
                "first_order_at": row[2],
                "last_order_at": row[3],
            }
            for row in result.fetchall()
        ]
