from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum as SQLAlchemyEnum

from app.db.models.base import Base


# Enum for item statuses.
class ItemStatus(Enum):
    ORDERED = 1
    PREPARING = 2
    READY = 3


class ItemStatusHistory(Base):
    __tablename__ = "item_status_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    item_id = Column(
        UUID(as_uuid=True), ForeignKey("items.id"), nullable=False, index=True
    )

    status = Column(SQLAlchemyEnum(ItemStatus), nullable=False)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    item = relationship("Item", back_populates="status_history")
