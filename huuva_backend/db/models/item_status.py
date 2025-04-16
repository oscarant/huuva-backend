from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Enum as SQLAlchemyEnum

from huuva_backend.db.base import Base

if TYPE_CHECKING:
    from huuva_backend.db.models.item import Item


class ItemStatus(Enum):
    ORDERED = 1
    PREPARING = 2
    READY = 3


class ItemStatusHistory(Base):
    __tablename__ = "item_status_history"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    order_id: Mapped[UUID] = mapped_column(
        PG_UUID,
        ForeignKey("items.order_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_plu: Mapped[str] = mapped_column(
        ForeignKey("items.plu", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[ItemStatus] = mapped_column(
        SQLAlchemyEnum(ItemStatus, native_enum=False),
        nullable=False,
    )
    timestamp: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    item: Mapped[Item] = relationship(
        back_populates="status_history",
        primaryjoin="and_(ItemStatusHistory.order_id==Item.order_id,"
        "ItemStatusHistory.plu==Item.plu)",
    )
