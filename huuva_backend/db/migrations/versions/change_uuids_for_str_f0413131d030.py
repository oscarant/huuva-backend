"""Change UUIDs for str.

Revision ID: f0413131d030
Revises: 9219e061d5b4
Create Date: 2025-04-18 01:15:15.604088

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f0413131d030"
down_revision = "9219e061d5b4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1) Drop foreign key constraints
    op.drop_constraint(
        "item_status_history_order_id_item_plu_fkey",
        "item_status_history",
        type_="foreignkey",
    )
    op.drop_constraint(
        "items_order_id_fkey",
        "items",
        type_="foreignkey",
    )
    op.drop_constraint(
        "order_status_history_order_id_fkey",
        "order_status_history",
        type_="foreignkey",
    )

    # 2) Alter columns, using USING to cast existing UUID → text
    op.alter_column(
        "orders",
        "id",
        type_=sa.String(),
        existing_type=sa.UUID(),
        postgresql_using="id::text",
        nullable=False,
    )
    op.alter_column(
        "orders",
        "account",
        type_=sa.String(),
        existing_type=sa.UUID(),
        postgresql_using="account::text",
        nullable=False,
    )
    op.alter_column(
        "orders",
        "brand_id",
        type_=sa.String(),
        existing_type=sa.UUID(),
        postgresql_using="brand_id::text",
        nullable=False,
    )
    op.alter_column(
        "items",
        "order_id",
        type_=sa.String(),
        existing_type=sa.UUID(),
        postgresql_using="order_id::text",
        nullable=False,
    )
    op.alter_column(
        "item_status_history",
        "order_id",
        type_=sa.String(),
        existing_type=sa.UUID(),
        postgresql_using="order_id::text",
        nullable=False,
    )
    op.alter_column(
        "order_status_history",
        "order_id",
        type_=sa.String(),
        existing_type=sa.UUID(),
        postgresql_using="order_id::text",
        nullable=False,
    )

    # 3) Re-create the foreign key constraints
    op.create_foreign_key(
        "items_order_id_fkey",
        "items",
        "orders",
        ["order_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "item_status_history_order_id_item_plu_fkey",
        "item_status_history",
        "items",
        ["order_id", "item_plu"],
        ["order_id", "plu"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "order_status_history_order_id_fkey",
        "order_status_history",
        "orders",
        ["order_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    # Drop new FKs
    op.drop_constraint(
        "item_status_history_order_id_item_plu_fkey",
        "item_status_history",
        type_="foreignkey",
    )
    op.drop_constraint(
        "items_order_id_fkey",
        "items",
        type_="foreignkey",
    )
    op.drop_constraint(
        "order_status_history_order_id_fkey",
        "order_status_history",
        type_="foreignkey",
    )

    # Revert columns back to UUID (using cast)
    op.alter_column(
        "order_status_history",
        "order_id",
        type_=sa.UUID(),
        existing_type=sa.String(),
        postgresql_using="order_id::uuid",
        nullable=False,
    )
    op.alter_column(
        "item_status_history",
        "order_id",
        type_=sa.UUID(),
        existing_type=sa.String(),
        postgresql_using="order_id::uuid",
        nullable=False,
    )
    op.alter_column(
        "items",
        "order_id",
        type_=sa.UUID(),
        existing_type=sa.String(),
        postgresql_using="order_id::uuid",
        nullable=False,
    )
    op.alter_column(
        "orders",
        "brand_id",
        type_=sa.UUID(),
        existing_type=sa.String(),
        postgresql_using="brand_id::uuid",
        nullable=False,
    )
    op.alter_column(
        "orders",
        "account",
        type_=sa.UUID(),
        existing_type=sa.String(),
        postgresql_using="account::uuid",
        nullable=False,
    )
    op.alter_column(
        "orders",
        "id",
        type_=sa.UUID(),
        existing_type=sa.String(),
        postgresql_using="id::uuid",
        nullable=False,
    )

    # Re-create the original foreign key constraints
    op.create_foreign_key(
        "items_order_id_fkey",
        "items",
        "orders",
        ["order_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "item_status_history_order_id_item_plu_fkey",
        "item_status_history",
        "items",
        ["order_id", "item_plu"],
        ["order_id", "plu"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "order_status_history_order_id_fkey",
        "order_status_history",
        "orders",
        ["order_id"],
        ["id"],
        ondelete="CASCADE",
    )
