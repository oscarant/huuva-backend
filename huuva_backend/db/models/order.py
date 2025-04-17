from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List
from uuid import uuid4

from sqlalchemy import TIMESTAMP, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Enum as SQLAlchemyEnum

from huuva_backend.db.base import Base
from huuva_backend.db.models.order_status import OrderStatus

if TYPE_CHECKING:
    from huuva_backend.db.models.item import Item
    from huuva_backend.db.models.order_status import OrderStatusHistory


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        Index(
            "ix_orders_account",
            "account",
            unique=False,
        ),
        Index(
            "ix_created_at",
            "created_at",
            unique=False,
        ),
    )

    id: Mapped[str] = mapped_column(
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    account: Mapped[str] = mapped_column(
        nullable=False,
    )
    brand_id: Mapped[str] = mapped_column(nullable=False)
    channel_order_id: Mapped[str] = mapped_column(String, nullable=False)

    customer_name: Mapped[str] = mapped_column(String, nullable=False)
    customer_phone: Mapped[str] = mapped_column(String, nullable=False)

    pickup_time: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    status: Mapped[OrderStatus] = mapped_column(
        SQLAlchemyEnum(OrderStatus, native_enum=False),
        default=OrderStatus.RECEIVED,
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
