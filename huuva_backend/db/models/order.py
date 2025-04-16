from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List
from uuid import UUID, uuid4

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Enum as SQLAlchemyEnum

from huuva_backend.db.base import Base
from huuva_backend.db.models.order_status import OrderStatus

if TYPE_CHECKING:
    from huuva_backend.db.models.item import Item
    from huuva_backend.db.models.order_status import OrderStatusHistory


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    account: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    brand_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    channel_order_id: Mapped[str] = mapped_column(String, nullable=False)

    customer_name: Mapped[str] = mapped_column(String, nullable=False)
    customer_phone: Mapped[str] = mapped_column(String, nullable=False)

    pickup_time: Mapped[datetime] = mapped_column(nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        SQLAlchemyEnum(OrderStatus, native_enum=False),
        nullable=False,
    )

    delivery_city: Mapped[str] = mapped_column(String, nullable=False)
    delivery_street: Mapped[str] = mapped_column(String, nullable=False)
    delivery_postal_code: Mapped[str] = mapped_column(String, nullable=False)

    items: Mapped[List["Item"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )
    status_history: Mapped[List["OrderStatusHistory"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )
