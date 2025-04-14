from app.core.entities.order import Customer, DeliveryAddress
from app.core.entities.order import Order as OrderEntity
from app.core.entities.order import OrderCreate
from app.core.entities.order_status import OrderStatusHistory
from app.db.mappings.item import item_db_to_entity
from app.db.models.order import Order


def order_create_to_db(order_create: OrderCreate) -> Order:
    """
    Convert an OrderCreate schema to a database model Order.
    """
    order = Order(
        id=order_create.id,
        account=order_create.account,
        brand_id=order_create.brand_id,
        channel_order_id=order_create.channel_order_id,
        customer_name=order_create.customer.name,
        customer_phone=order_create.customer.phone_number,
        delivery_city=order_create.delivery_address.city,
        delivery_street=order_create.delivery_address.street,
        delivery_postal_code=order_create.delivery_address.postal_code,
        pickup_time=order_create.pickup_time,
        status=order_create.status,
    )
    return order


def order_db_to_entity(order: Order) -> OrderEntity:
    """
    Convert a database model Order to an Order entity.
    """
    order_entity = OrderEntity(
        id=order.id,
        created_at=order.created_at,
        updated_at=order.updated_at,
        account=order.account,
        brand_id=order.brand_id,
        channel_order_id=order.channel_order_id,
        customer=Customer(
            name=order.customer_name,
            phone_number=order.customer_phone,
        ),
        delivery_address=DeliveryAddress(
            city=order.delivery_city,
            street=order.delivery_street,
            postal_code=order.delivery_postal_code,
        ),
        pickup_time=order.pickup_time,
        items=[item_db_to_entity(item) for item in order.items],
        status=order.status,
        status_history=[
            OrderStatusHistory.model_validate(hist) for hist in order.status_history
        ],
    )
    return order_entity
