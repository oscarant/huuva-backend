"""add_analytics_views.

Revision ID: 3ed2f5cf77e5
Revises: 79a1132de7f3
Create Date: 2025-04-18 10:53:08.028418

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "3ed2f5cf77e5"
down_revision = "79a1132de7f3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Average time spent in each status for orders
    op.execute(
        """
    CREATE MATERIALIZED VIEW order_status_duration_avg AS
    WITH status_periods AS (
        SELECT
            order_id,
            status,
            timestamp AS start_time,
            LEAD(timestamp) OVER (PARTITION BY order_id ORDER BY timestamp) AS end_time
        FROM order_status_history
    )
    SELECT
        status,
        AVG(EXTRACT(EPOCH FROM (end_time - start_time))) AS avg_duration_seconds
    FROM status_periods
    WHERE
        end_time IS NOT NULL
        AND status IN ('RECEIVED', 'PREPARING', 'READY')  -- Only non-terminal statuses: RECEIVED, PREPARING, READY
    GROUP BY status;
    """
    )

    # 2. Average time spent in each status for items
    op.execute(
        """
    CREATE MATERIALIZED VIEW item_status_duration_avg AS
    WITH status_periods AS (
        SELECT
            order_id,
            item_plu,
            status,
            timestamp AS start_time,
            LEAD(timestamp) OVER (PARTITION BY order_id, item_plu ORDER BY timestamp) AS end_time
        FROM item_status_history
    )
    SELECT
        status,
        AVG(EXTRACT(EPOCH FROM (end_time - start_time))) AS avg_duration_seconds
    FROM status_periods
    WHERE
        end_time IS NOT NULL
        AND status IN ('ORDERED', 'PREPARING', 'READY')  -- Only non-terminal statuses: ORDERED, PREPARING, READY
    GROUP BY status;
    """
    )

    # 3. Order throughput per hour
    op.execute(
        """
    CREATE MATERIALIZED VIEW order_hourly_throughput AS
    SELECT
        DATE_TRUNC('hour', created_at) AS hour,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY DATE_TRUNC('hour', created_at)
    ORDER BY hour;
    """
    )

    # 4. Number of orders per customer lifetime
    op.execute(
        """
    CREATE MATERIALIZED VIEW customer_order_count AS
    SELECT
        account,
        COUNT(*) AS order_count,
        MIN(created_at) AS first_order_at,
        MAX(created_at) AS last_order_at
    FROM orders
    GROUP BY account;
    """
    )

    # Add indexes to the materialized views for faster querying
    op.execute(
        "CREATE INDEX idx_order_status_duration_avg_status ON order_status_duration_avg (status);"
    )
    op.execute(
        "CREATE INDEX idx_item_status_duration_avg_status ON item_status_duration_avg (status);"
    )
    op.execute(
        "CREATE INDEX idx_order_hourly_throughput_hour ON order_hourly_throughput (hour);"
    )
    op.execute(
        "CREATE INDEX idx_customer_order_count_account ON customer_order_count (account);"
    )


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS order_status_duration_avg;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS item_status_duration_avg;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS order_hourly_throughput;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS customer_order_count;")
