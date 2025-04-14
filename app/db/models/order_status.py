from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum as SQLAlchemyEnum

from app.db.models.base import Base


# Enum for order statuses.
class OrderStatus(Enum):
    RECEIVED = 1
    PREPARING = 2
    READY = 3
    PICKED_UP = 4
    CANCELLED = 5


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    order_id = Column(
        UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False, index=True
    )

    status = Column(SQLAlchemyEnum(OrderStatus, native_enum=False), nullable=False)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    order = relationship("Order", back_populates="status_history")
