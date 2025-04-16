"""create order system models.

Revision ID: f15e66159415
Revises:
Create Date: 2025-04-16 23:00:28.352382

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f15e66159415"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Run the migration."""
    op.create_table(
        "orders",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("account", sa.UUID(), nullable=False),
        sa.Column("brand_id", sa.UUID(), nullable=False),
        sa.Column("channel_order_id", sa.String(), nullable=False),
        sa.Column("customer_name", sa.String(), nullable=False),
        sa.Column("customer_phone", sa.String(), nullable=False),
        sa.Column("pickup_time", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("delivery_city", sa.String(), nullable=False),
        sa.Column("delivery_street", sa.String(), nullable=False),
        sa.Column("delivery_postal_code", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_orders_account"), "orders", ["account"], unique=False)
    op.create_index((op.f("ix_created_at")), "orders", ["created_at"], unique=False)

    op.create_table(
        "items",
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("plu", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("order_id", "plu"),
    )

    op.create_table(
        "order_status_history",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_order_status_history_order_id"),
        "order_status_history",
        ["order_id"],
        unique=False,
    )

    op.create_table(
        "item_status_history",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("item_plu", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["order_id", "item_plu"],
            ["items.order_id", "items.plu"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_item_status_history_order_id_item_plu",
        "item_status_history",
        ["order_id", "item_plu"],
        unique=True,
    )


def downgrade() -> None:
    """Undo the migration."""
    op.drop_index(
        op.f("ix_item_status_history_item_id"),
        table_name="item_status_history",
    )
    op.drop_table("item_status_history")
    op.drop_index(
        op.f("ix_order_status_history_order_id"),
        table_name="order_status_history",
    )
    op.drop_table("order_status_history")
    op.drop_table("items")
    op.drop_index(op.f("ix_orders_account"), table_name="orders")
    op.drop_table("orders")
