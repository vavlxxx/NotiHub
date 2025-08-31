"""new: SMS contact type

Revision ID: de5883a39339
Revises: 6fe03ac71b14
Create Date: 2025-08-31 11:08:27.701592

"""

from typing import Sequence, Union

from alembic import op
from alembic_postgresql_enum import TableReference

# revision identifiers, used by Alembic.
revision: str = "de5883a39339"
down_revision: Union[str, Sequence[str], None] = "6fe03ac71b14"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.sync_enum_values(  # type: ignore
        enum_schema="public",
        enum_name="contactchanneltype",
        new_values=["EMAIL", "TELEGRAM", "PUSH", "SMS"],
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
    op.sync_enum_values(  # type: ignore
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
