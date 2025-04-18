"""Change last UUID to str.

Revision ID: 79a1132de7f3
Revises: f0413131d030
Create Date: 2025-04-18 10:51:49.852108

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "79a1132de7f3"
down_revision = "f0413131d030"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Run the migration."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "item_status_history",
        "id",
        existing_type=sa.UUID(),
        type_=sa.String(),
        existing_nullable=False,
    )
    op.alter_column(
        "item_status_history",
        "timestamp",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.TIMESTAMP(timezone=True),
        existing_nullable=False,
    )
    op.alter_column(
        "order_status_history",
        "id",
        existing_type=sa.UUID(),
        type_=sa.String(),
        existing_nullable=False,
    )
    op.alter_column(
        "order_status_history",
        "timestamp",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.TIMESTAMP(timezone=True),
        existing_nullable=False,
    )
    op.alter_column(
        "orders",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.TIMESTAMP(timezone=True),
        existing_nullable=False,
    )
    op.alter_column(
        "orders",
        "updated_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.TIMESTAMP(timezone=True),
        existing_nullable=False,
    )
    op.alter_column(
        "orders",
        "pickup_time",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.TIMESTAMP(timezone=True),
        existing_nullable=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Undo the migration."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "orders",
        "pickup_time",
        existing_type=sa.TIMESTAMP(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )
    op.alter_column(
        "orders",
        "updated_at",
        existing_type=sa.TIMESTAMP(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )
    op.alter_column(
        "orders",
        "created_at",
        existing_type=sa.TIMESTAMP(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )
    op.alter_column(
        "order_status_history",
        "timestamp",
        existing_type=sa.TIMESTAMP(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )
    op.alter_column(
        "order_status_history",
        "id",
        existing_type=sa.String(),
        type_=sa.UUID(),
        existing_nullable=False,
    )
    op.alter_column(
        "item_status_history",
        "timestamp",
        existing_type=sa.TIMESTAMP(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )
    op.alter_column(
        "item_status_history",
        "id",
        existing_type=sa.String(),
        type_=sa.UUID(),
        existing_nullable=False,
    )
    # ### end Alembic commands ###
