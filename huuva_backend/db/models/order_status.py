from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Enum as SQLAlchemyEnum

from huuva_backend.db.base import Base
from huuva_backend.db.models.order import Order


# Enum for order statuses.
class OrderStatus(Enum):
    RECEIVED = 1
    PREPARING = 2
    READY = 3
    PICKED_UP = 4
    CANCELLED = 5


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    order_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        index=True,
    )
    status: Mapped[OrderStatus] = mapped_column(
        SQLAlchemyEnum(OrderStatus, native_enum=False),
        nullable=False,
    )
    timestamp: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    order: Mapped["Order"] = relationship(back_populates="status_history")
