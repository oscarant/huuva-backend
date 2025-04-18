import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from huuva_backend.services.analytics import AnalyticsService

logger = logging.getLogger(__name__)


class AnalyticsScheduler:
    """Scheduler for analytics data aggregation jobs."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory
        self.scheduler = AsyncIOScheduler()

    async def refresh_materialized_views(self) -> None:
        """Job to refresh all materialized views."""
        logger.info("Starting materialized views refresh job at %s", datetime.now())
        try:
            session: AsyncSession = self.session_factory()
            analytics_service = AnalyticsService(session)

            await analytics_service.refresh_materialized_views()
            logger.info("Successfully refreshed materialized views")
        except Exception as e:
            logger.error("Error refreshing materialized views: %s", str(e))
        finally:
            await session.close()

    def start(self) -> None:
        """Start the scheduler."""
        # Schedule the job to run every hour
        self.scheduler.add_job(
            self.refresh_materialized_views,
            "interval",
            hours=1,
            id="refresh_materialized_views",
            replace_existing=True,
        )

        # Also schedule an immediate run when the application starts
        self.scheduler.add_job(
            self.refresh_materialized_views,
            "date",
            run_date=datetime.now(),
            id="refresh_materialized_views_initial",
            replace_existing=True,
        )

        self.scheduler.start()
        logger.info("Analytics scheduler started")

    def shutdown(self) -> None:
        """Shutdown the scheduler."""
        self.scheduler.shutdown()
        logger.info("Analytics scheduler shut down")
