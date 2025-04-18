from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from huuva_backend.scheduler import AnalyticsScheduler
from huuva_backend.settings import settings


def _setup_db(app: FastAPI) -> None:  # pragma: no cover
    """
    Creates connection to the database.

    This function creates SQLAlchemy engine instance,
    session_factory for creating sessions
    and stores them in the application's state property.

    :param app: fastAPI application.
    """
    engine = create_async_engine(str(settings.db_url), echo=settings.db_echo)
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )
    app.state.db_engine = engine
    app.state.db_session_factory = session_factory


def _setup_scheduler(app: FastAPI) -> None:
    """
    Set up the analytics scheduler.

    :param app: fastAPI application.
    """
    scheduler = AnalyticsScheduler(app.state.db_session_factory)
    app.state.scheduler = scheduler
    scheduler.start()


@asynccontextmanager
async def lifespan_setup(
    app: FastAPI,
) -> AsyncGenerator[None, None]:  # pragma: no cover
    """
    Actions to run on application startup.

    This function uses fastAPI app to store data
    in the state, such as db_engine.

    :param app: the fastAPI application.
    :return: function that actually performs actions.
    """

    app.middleware_stack = None
    _setup_db(app)
    app.middleware_stack = app.build_middleware_stack()

    # Set up and start the scheduler after db is initialized
    _setup_scheduler(app)

    yield
    # Shutdown scheduler before closing db connection
    app.state.scheduler.shutdown()
    await app.state.db_engine.dispose()
