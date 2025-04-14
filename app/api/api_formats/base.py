from pydantic import BaseModel


class BaseSchema(BaseModel):
    """Base schema for input models (no ORM mode)."""

    class Config:
        orm_mode = False


class OrmSchema(BaseModel):
    """Base schema for response models (ORM mode enabled)."""

    class Config:
        orm_mode = True
