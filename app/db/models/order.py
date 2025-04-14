from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum as SQLAlchemyEnum

from app.db.models.base import Base
from app.db.models.order_status import OrderStatus


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
        nullable=False,
    )

    account = Column(UUID(as_uuid=True), nullable=False, index=True)
    brand_id = Column(UUID(as_uuid=True), nullable=False)
    channel_order_id = Column(String, nullable=False)

    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)

    pickup_time = Column(DateTime, nullable=False)
    status = Column(SQLAlchemyEnum(OrderStatus, native_enum=False), nullable=False)

    delivery_city = Column(String, nullable=False)
    delivery_street = Column(String, nullable=False)
    delivery_postal_code = Column(String, nullable=False)

    items = relationship("Item", back_populates="order", cascade="all, delete-orphan")
    status_history = relationship(
        "OrderStatusHistory", back_populates="order", cascade="all, delete-orphan"
    )
