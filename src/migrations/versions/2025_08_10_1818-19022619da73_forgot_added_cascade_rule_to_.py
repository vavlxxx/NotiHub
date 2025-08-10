"""forgot: added CASCADE rule to Notification relationships

Revision ID: 19022619da73
Revises: d46d8e75b97e
Create Date: 2025-08-10 18:18:39.676964

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "19022619da73"
down_revision: Union[str, Sequence[str], None] = "d46d8e75b97e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        op.f("fk_notification_channels_notification_id_notifications"),
        "notification_channels",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_notification_channels_channel_id_user_contact_channels"),
        "notification_channels",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("fk_notification_channels_channel_id_user_contact_channels"),
        "notification_channels",
        "user_contact_channels",
        ["channel_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_notification_channels_notification_id_notifications"),
        "notification_channels",
        "notifications",
        ["notification_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint(
        op.f("fk_notification_variables_notification_id_notifications"),
        "notification_variables",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("fk_notification_variables_notification_id_notifications"),
        "notification_variables",
        "notifications",
        ["notification_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        op.f("fk_notification_variables_notification_id_notifications"),
        "notification_variables",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("fk_notification_variables_notification_id_notifications"),
        "notification_variables",
        "notifications",
        ["notification_id"],
        ["id"],
    )
    op.drop_constraint(
        op.f("fk_notification_channels_notification_id_notifications"),
        "notification_channels",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_notification_channels_channel_id_user_contact_channels"),
        "notification_channels",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("fk_notification_channels_channel_id_user_contact_channels"),
        "notification_channels",
        "user_contact_channels",
        ["channel_id"],
        ["id"],
    )
    op.create_foreign_key(
        op.f("fk_notification_channels_notification_id_notifications"),
        "notification_channels",
        "notifications",
        ["notification_id"],
        ["id"],
    )
