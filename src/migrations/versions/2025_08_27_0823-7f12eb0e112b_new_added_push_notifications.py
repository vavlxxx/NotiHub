"""new: added push notifications

Revision ID: 7f12eb0e112b
Revises: 8cbc5d1daf4c
Create Date: 2025-08-27 08:23:36.445249

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from alembic_postgresql_enum import TableReference

# revision identifiers, used by Alembic.
revision: str = "7f12eb0e112b"
down_revision: Union[str, Sequence[str], None] = "8cbc5d1daf4c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "notification_logs",
        sa.Column(
            "details",
            sa.String(),
            nullable=True,
            comment="Ответ от провайдера",
        ),
    )
    op.drop_column("notification_logs", "provider_response")
    op.sync_enum_values(
        enum_schema="public",
        enum_name="contactchanneltype",
        new_values=["EMAIL", "TELEGRAM", "PUSH"],
        affected_columns=[
            TableReference(
                table_schema="public",
                table_name="notification_logs",
                column_name="provider_name",
            ),
            TableReference(
                table_schema="public",
                table_name="user_contact_channels",
                column_name="channel_type",
            ),
        ],
        enum_values_to_rename=[],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.sync_enum_values(
        enum_schema="public",
        enum_name="contactchanneltype",
        new_values=["EMAIL", "TELEGRAM"],
        affected_columns=[
            TableReference(
                table_schema="public",
                table_name="notification_logs",
                column_name="provider_name",
            ),
            TableReference(
                table_schema="public",
                table_name="user_contact_channels",
                column_name="channel_type",
            ),
        ],
        enum_values_to_rename=[],
    )
    op.add_column(
        "notification_logs",
        sa.Column(
            "provider_response",
            sa.VARCHAR(),
            autoincrement=False,
            nullable=True,
            comment="Ответ от провайдера",
        ),
    )
    op.drop_column("notification_logs", "details")
