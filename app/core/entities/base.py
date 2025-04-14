from pydantic import BaseModel


class BaseSchema(BaseModel):
    """Base schema for input models (no ORM mode)."""

    class Config:
        from_attributes = False


class OrmSchema(BaseModel):
    """Base schema for response models (ORM mode enabled)."""

    class Config:
        from_attributes = True
