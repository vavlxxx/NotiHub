"""forgot: added user_id to notification and receiver to noti_logs

Revision ID: d46d8e75b97e
Revises: 4ac68aa8dded
Create Date: 2025-08-10 17:01:23.810813

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d46d8e75b97e"
down_revision: Union[str, Sequence[str], None] = "4ac68aa8dded"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "notification_logs", sa.Column("receiver", sa.String(), nullable=False)
    )
    op.alter_column(
        "notification_logs",
        "response",
        existing_type=sa.VARCHAR(),
        nullable=False,
    )
    op.add_column(
        "notifications", sa.Column("user_id", sa.Integer(), nullable=False)
    )
    op.create_unique_constraint(
        "unique_user_template", "notifications", ["user_id", "template_id"]
    )
    op.create_foreign_key(
        op.f("fk_notifications_user_id_users"),
        "notifications",
        "users",
        ["user_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        op.f("fk_notifications_user_id_users"),
        "notifications",
        type_="foreignkey",
    )
    op.drop_constraint("unique_user_template", "notifications", type_="unique")
    op.drop_column("notifications", "user_id")
    op.alter_column(
        "notification_logs",
        "response",
        existing_type=sa.VARCHAR(),
        nullable=True,
    )
    op.drop_column("notification_logs", "receiver")
