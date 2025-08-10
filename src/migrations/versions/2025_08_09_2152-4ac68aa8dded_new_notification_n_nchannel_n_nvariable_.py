"""new: Notification, N-nChannel, N-nVariable, N-nLog

Revision ID: 4ac68aa8dded
Revises: a36645894a72
Create Date: 2025-08-09 21:52:33.661185

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4ac68aa8dded"
down_revision: Union[str, Sequence[str], None] = "a36645894a72"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "notification_logs",
        sa.Column("sended_message", sa.String(), nullable=False),
        sa.Column("response", sa.String(), nullable=True),
        sa.Column(
            "sent_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_notification_logs")),
    )
    op.create_table(
        "notifications",
        sa.Column("template_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["template_id"],
            ["templates.id"],
            name=op.f("fk_notifications_template_id_templates"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_notifications")),
    )
    op.create_table(
        "notification_channels",
        sa.Column("notification_id", sa.Integer(), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["user_contact_channels.id"],
            name=op.f(
                "fk_notification_channels_channel_id_user_contact_channels"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["notification_id"],
            ["notifications.id"],
            name=op.f(
                "fk_notification_channels_notification_id_notifications"
            ),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_notification_channels")),
    )
    op.create_table(
        "notification_variables",
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("value", sa.String(), nullable=False),
        sa.Column("notification_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["notification_id"],
            ["notifications.id"],
            name=op.f(
                "fk_notification_variables_notification_id_notifications"
            ),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_notification_variables")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("notification_variables")
    op.drop_table("notification_channels")
    op.drop_table("notifications")
    op.drop_table("notification_logs")
