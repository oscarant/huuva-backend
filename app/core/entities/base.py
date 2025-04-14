from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema for input models"""

    model_config = ConfigDict(from_attributes=False)


class OrmSchema(BaseModel):
    """Base schema for response models"""

    model_config = ConfigDict(from_attributes=True)
