from datetime import datetime

from huuva_backend.web.api.api_formats.base import OrmSchema


class StatusDuration(OrmSchema):
    status: str
    avg_duration_seconds: float


class HourlyThroughput(OrmSchema):
    hour: datetime
    order_count: int


class CustomerOrderCount(OrmSchema):
    account: str
    order_count: int
    first_order_at: datetime
    last_order_at: datetime
