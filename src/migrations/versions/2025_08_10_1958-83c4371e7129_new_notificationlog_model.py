"""new: NotificationLog model

Revision ID: 83c4371e7129
Revises: a36645894a72
Create Date: 2025-08-10 19:58:31.368607

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "83c4371e7129"
down_revision: Union[str, Sequence[str], None] = "a36645894a72"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "notification_logs",
        sa.Column("receiver", sa.String(), nullable=False),
        sa.Column("response", sa.String(), nullable=False),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column(
            "sent_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_notification_logs")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("notification_logs")
