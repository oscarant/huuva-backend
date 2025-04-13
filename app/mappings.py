from app.models.order import ItemStatus as ModelItemStatus
from app.models.order import OrderStatus as ModelOrderStatus
from app.schemas.order import ItemStatus as SchemaItemStatus
from app.schemas.order import OrderStatus as SchemaOrderStatus


def map_order_status(schema_status: SchemaOrderStatus) -> ModelOrderStatus:
    """
    Convert a schema OrderStatus to a model OrderStatus.
    """
    # You can convert using the numeric value or the name.
    return ModelOrderStatus(schema_status.value)
    # Alternatively:
    # return ModelOrderStatus[schema_status.name]


def map_item_status(schema_status: SchemaItemStatus) -> ModelItemStatus:
    """
    Convert a schema ItemStatus to a model ItemStatus.
    """
    return ModelItemStatus(schema_status.value)
    # Alternatively:
    # return ModelItemStatus[schema_status.name]
