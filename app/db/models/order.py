from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum as SQLAlchemyEnum

from app.models.base import Base


# Enum for order statuses.
class OrderStatus(Enum):
    RECEIVED = 1
    PREPARING = 2
    READY = 3
    PICKED_UP = 4
    CANCELLED = 5


class ItemStatus(Enum):
    ORDERED = 1
    PREPARING = 2
    READY = 3


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
    status = Column(SQLAlchemyEnum(OrderStatus), nullable=False)

    delivery_city = Column(String, nullable=False)
    delivery_street = Column(String, nullable=False)
    delivery_postal_code = Column(String, nullable=False)

    items = relationship("Item", back_populates="order", cascade="all, delete-orphan")
    status_history = relationship(
        "OrderStatusHistory", back_populates="order", cascade="all, delete-orphan"
    )


class Item(Base):
    __tablename__ = "items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    order_id = Column(
        UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False, index=True
    )

    name = Column(String, nullable=False)
    plu = Column(String, nullable=False, index=True)
    quantity = Column(Integer, nullable=False)

    status = Column(
        SQLAlchemyEnum(ItemStatus), nullable=False, default=ItemStatus.ORDERED
    )

    order = relationship("Order", back_populates="items")
    status_history = relationship(
        "ItemStatusHistory", back_populates="item", cascade="all, delete-orphan"
    )


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    order_id = Column(
        UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False, index=True
    )

    status = Column(SQLAlchemyEnum(OrderStatus), nullable=False)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    order = relationship("Order", back_populates="status_history")


class ItemStatusHistory(Base):
    __tablename__ = "item_status_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    item_id = Column(
        UUID(as_uuid=True), ForeignKey("items.id"), nullable=False, index=True
    )

    status = Column(SQLAlchemyEnum(ItemStatus), nullable=False)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    item = relationship("Item", back_populates="status_history")
