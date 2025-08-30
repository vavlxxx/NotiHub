"""logs: added sender_id + PENDING status + created_at to NotificationLogs

Revision ID: 6fe03ac71b14
Revises: 7f12eb0e112b
Create Date: 2025-08-30 18:23:07.355421

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from alembic_postgresql_enum import TableReference
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "6fe03ac71b14"
down_revision: Union[str, Sequence[str], None] = "7f12eb0e112b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "notification_logs",
        sa.Column("sender_id", sa.Integer(), nullable=False),
    )
    op.add_column(
        "notification_logs",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.alter_column(
        "notification_logs",
        "delivered_at",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=True,
        existing_server_default=sa.text("now()"),
    )
    op.sync_enum_values(  # type: ignore
        enum_schema="public",
        enum_name="notificationstatus",
        new_values=["SUCCESS", "FAILURE", "PENDING"],
        affected_columns=[
            TableReference(
                table_schema="public",
                table_name="notification_logs",
                column_name="status",
            )
        ],
        enum_values_to_rename=[],
    )
    op.create_index(
        "unique_pending_notifications",
        "notification_logs",
        ["sender_id", "contact_data", "message", "provider_name"],
        unique=True,
        postgresql_where="status = 'PENDING'",
    )
    op.create_foreign_key(
        op.f("fk_notification_logs_sender_id_users"),
        "notification_logs",
        "users",
        ["sender_id"],
        ["id"],
        onupdate="cascade",
        ondelete="cascade",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.sync_enum_values(  # type: ignore
        enum_schema="public",
        enum_name="notificationstatus",
        new_values=["SUCCESS", "FAILURE"],
        affected_columns=[
            TableReference(
                table_schema="public",
                table_name="notification_logs",
                column_name="status",
            )
        ],
        enum_values_to_rename=[],
    )
    op.drop_constraint(
        op.f("fk_notification_logs_sender_id_users"),
        "notification_logs",
        type_="foreignkey",
    )
    op.drop_index(
        "unique_pending_notifications",
        table_name="notification_logs",
        postgresql_where="status = 'PENDING'",
    )
    op.alter_column(
        "notification_logs",
        "delivered_at",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=False,
        existing_server_default=sa.text("now()"),
    )
    op.drop_column("notification_logs", "created_at")
    op.drop_column("notification_logs", "sender_id")
