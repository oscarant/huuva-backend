from __future__ import annotations

from datetime import datetime
from enum import IntEnum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKeyConstraint, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Enum as SQLAlchemyEnum

from huuva_backend.db.base import Base

if TYPE_CHECKING:
    from huuva_backend.db.models.item import Item


class ItemStatus(IntEnum):
    ORDERED = 1
    PREPARING = 2
    READY = 3


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

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    order_id: Mapped[UUID] = mapped_column(
        PG_UUID,
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
        DateTime,
        default=lambda: datetime.now(),
        nullable=False,
    )

    item: Mapped[Item] = relationship(
        back_populates="status_history",
        primaryjoin="and_(ItemStatusHistory.order_id==Item.order_id,"
        "ItemStatusHistory.item_plu==Item.plu)",
    )
