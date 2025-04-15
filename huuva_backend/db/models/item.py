from typing import List
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Enum as SQLAlchemyEnum

from huuva_backend.db.base import Base
from huuva_backend.db.models.item_status import ItemStatus, ItemStatusHistory
from huuva_backend.db.models.order import Order


class Item(Base):
    __tablename__ = "items"

    order_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        default=uuid4,
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
