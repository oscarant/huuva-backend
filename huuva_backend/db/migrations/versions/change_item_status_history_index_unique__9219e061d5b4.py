"""change item status history  index unique to false.

Revision ID: 9219e061d5b4
Revises: f15e66159415
Create Date: 2025-04-17 11:07:20.362065

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "9219e061d5b4"
down_revision = "f15e66159415"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Run the migration."""
    op.drop_index(
        "ix_item_status_history_order_id_item_plu",
        table_name="item_status_history",
    )
    op.create_index(
        "ix_item_status_history_order_id_item_plu",
        "item_status_history",
        ["order_id", "item_plu"],
        unique=False,
    )


def downgrade() -> None:
    """Undo the migration."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        "ix_item_status_history_order_id_item_plu",
        table_name="item_status_history",
    )
    op.create_index(
        "ix_item_status_history_order_id_item_plu",
        "item_status_history",
        ["order_id", "item_plu"],
        unique=True,
    )
    # ### end Alembic commands ###
