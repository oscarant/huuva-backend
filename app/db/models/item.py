from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum as SQLAlchemyEnum

from app.db.models.base import Base
from app.db.models.item_status import ItemStatus


class Item(Base):
    __tablename__ = "items"

    order_id = Column(
        UUID(as_uuid=True),
        ForeignKey("orders.id"),
        nullable=False,
    )
    plu = Column(String, nullable=False, primary_key=True)

    name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)

    status = Column(
        SQLAlchemyEnum(ItemStatus), nullable=False, default=ItemStatus.ORDERED
    )

    order = relationship("Order", back_populates="items")
    status_history = relationship(
        "ItemStatusHistory", back_populates="item", cascade="all, delete-orphan"
    )
