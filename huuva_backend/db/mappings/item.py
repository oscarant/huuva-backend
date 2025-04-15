from huuva_backend.core.entities.item import Item as ItemEntity
from huuva_backend.core.entities.item_status import ItemStatus as ItemStatusEntity
from huuva_backend.core.entities.item_status import ItemStatusHistory
from huuva_backend.db.models.item import Item


def item_db_to_entity(item_db: Item) -> ItemEntity:
    """Convert a DB Item model to an API Item entity."""
    return ItemEntity(
        name=item_db.name,
        plu=item_db.plu,
        quantity=item_db.quantity,
        status=ItemStatusEntity(item_db.status.value),
        status_history=[
            ItemStatusHistory.model_validate(hist) for hist in item_db.status_history
        ],
    )
