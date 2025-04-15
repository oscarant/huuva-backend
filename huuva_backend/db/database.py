from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from huuva_backend.config.settings import settings

# Create async SQLAlchemy engine
engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)

# Configure async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Dependency to retrieve a database session for API endpoints
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get a database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
