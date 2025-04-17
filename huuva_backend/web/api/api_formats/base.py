from enum import Enum

from pydantic import BaseModel, ConfigDict


def to_camel(string: str) -> str:
    """
    Convert a snake_case string to camelCase.

    E.g. 'delivery_address' → 'deliveryAddress'.
    """
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class BaseSchema(BaseModel):
    """
    All input schemas (for request bodies / query params) should subclass this.

    It will:
      • accept snake_case field names,
      • allow CamelCase in and out via the alias generator,
      • populate fields by attribute name or alias.
    """

    model_config = ConfigDict(
        from_attributes=False,
        alias_generator=to_camel,
        populate_by_name=True,
    )


class OrmSchema(BaseModel):
    """
    All response schemas should subclass this.

    It will:
      • read from ORM objects (`from_attributes=True`),
      • emit JSON using camelCase aliases,
      • serialize any Enum to its `.name` string.
    """

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        json_encoders={Enum: lambda e: e.name},
    )
