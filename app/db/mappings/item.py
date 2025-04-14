from app.core.entities.item import Item as ItemEntity
from app.core.entities.item_status import ItemStatusHistory
from app.db.models.item import Item


def item_db_to_entity(item_db: Item) -> ItemEntity:
    """
    Convert a DB Item model to an API Item entity.
    """
    return ItemEntity(
        name=item_db.name,
        plu=item_db.plu,
        quantity=item_db.quantity,
        status=item_db.status,
        status_history=[
            ItemStatusHistory.model_validate(hist, from_attributes=True)
            for hist in item_db.status_history
        ],
    )
