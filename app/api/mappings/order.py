from app.core.entities.item_status import ItemStatus as SchemaItemStatus
from app.core.entities.order_status import OrderStatus as SchemaOrderStatus
from app.db.models.item import ItemStatus as ModelItemStatus
from app.db.models.order import OrderStatus as ModelOrderStatus


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
