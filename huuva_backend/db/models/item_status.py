from __future__ import annotations

from datetime import datetime, timezone
from enum import IntEnum
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import TIMESTAMP, ForeignKeyConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Enum as SQLAlchemyEnum

from huuva_backend.db.base import Base

if TYPE_CHECKING:
    from huuva_backend.db.models.item import Item


class ItemStatus(IntEnum):
    ORDERED = 1
    PREPARING = 2
    READY = 3
    PICKED_UP = 4
    CANCELLED = 5


class ItemStatusHistory(Base):
    __tablename__ = "item_status_history"
    __table_args__ = (
        ForeignKeyConstraint(
            ["order_id", "item_plu"],
            ["items.order_id", "items.plu"],
            ondelete="CASCADE",
        ),
        Index(
            "ix_item_status_history_order_id_item_plu",
            "order_id",
            "item_plu",
            unique=False,
        ),
    )

    id: Mapped[str] = mapped_column(
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    order_id: Mapped[str] = mapped_column(
        nullable=False,
    )
    item_plu: Mapped[str] = mapped_column(
        nullable=False,
    )
    status: Mapped[ItemStatus] = mapped_column(
        SQLAlchemyEnum(ItemStatus, native_enum=False),
        nullable=False,
    )
    timestamp: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    item: Mapped[Item] = relationship(
        back_populates="status_history",
        primaryjoin="and_(ItemStatusHistory.order_id==Item.order_id,"
        "ItemStatusHistory.item_plu==Item.plu)",
    )
