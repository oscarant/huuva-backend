import sentry_sdk
from fastapi import FastAPI

from app.api.router.order import router as orders_router
from app.config.config import settings
from app.exceptions.error_handler import register_exception_handlers

# Initialize Sentry for error tracking and logging
if settings.SENTRY_DSN:
    sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=1.0)

app = FastAPI(title="Huuva Order Management API")
register_exception_handlers(app)

app.include_router(orders_router, prefix="/v1")
