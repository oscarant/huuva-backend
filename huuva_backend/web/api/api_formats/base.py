from pydantic import BaseModel, ConfigDict


def to_camel(string: str) -> str:
    """
    Convert a snake_case string to camelCase.

    E.g. 'delivery_address' → 'deliveryAddress'.
    """
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class BaseSchema(BaseModel):
    """Base schema for input models."""

    model_config = ConfigDict(
        from_attributes=False,
        alias_generator=to_camel,
        populate_by_name=True,
    )


class OrmSchema(BaseModel):
    """Base schema for response models."""

    model_config = ConfigDict(from_attributes=True)
