from __future__ import annotations

from typing import TYPE_CHECKING, List
from uuid import uuid4

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Enum as SQLAlchemyEnum

from huuva_backend.db.base import Base
from huuva_backend.db.models.item_status import ItemStatus

if TYPE_CHECKING:
    from huuva_backend.db.models.item_status import ItemStatusHistory
    from huuva_backend.db.models.order import Order


class Item(Base):
    __tablename__ = "items"

    order_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        default=lambda: str(uuid4()),
        primary_key=True,
    )
    plu: Mapped[str] = mapped_column(String, nullable=False, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[ItemStatus] = mapped_column(
        SQLAlchemyEnum(ItemStatus, native_enum=False),
        nullable=False,
        default=ItemStatus.ORDERED,
    )

    order: Mapped["Order"] = relationship(back_populates="items")
    status_history: Mapped[List["ItemStatusHistory"]] = relationship(
        back_populates="item",
        cascade="all, delete-orphan",
    )
