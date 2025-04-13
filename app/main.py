import sentry_sdk
from fastapi import FastAPI

from app.api.v1.orders import router as orders_router
from app.core.config import SENTRY_DSN

# Initialize Sentry for error tracking and logging
if SENTRY_DSN:
    sentry_sdk.init(dsn=SENTRY_DSN, traces_sample_rate=1.0)

app = FastAPI(title="Huuva Order Management API")

app.include_router(orders_router, prefix="/v1")
