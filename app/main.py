from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router.order import router as orders_router
from app.config.settings import settings
from app.db.database import engine
from app.exceptions.error_handler import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    await engine.dispose()


# Initialize Sentry for error tracking and logging
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=1.0,
        environment=settings.ENVIRONMENT,
    )

app = FastAPI(
    title="Huuva Order Management API",
    version="1.0.0",
    description="API for managing orders and items",
    lifespan=lifespan,
    openapi_url="/openapi.json" if not settings.PRODUCTION else None,
    docs_url="/docs" if not settings.PRODUCTION else None,
    redoc_url="/redoc" if not settings.PRODUCTION else None,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register handlers and routes
register_exception_handlers(app)
app.include_router(orders_router, prefix="/v1")
