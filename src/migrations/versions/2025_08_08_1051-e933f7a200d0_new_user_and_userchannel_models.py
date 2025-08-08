"""new: User and UserChannel models

Revision ID: e933f7a200d0
Revises: 4e0e14a100d3
Create Date: 2025-08-08 10:51:22.329544

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e933f7a200d0"
down_revision: Union[str, Sequence[str], None] = "4e0e14a100d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("first_name", sa.String(), nullable=True),
        sa.Column("last_name", sa.String(), nullable=True),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("notification_enabled", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("username", name=op.f("uq_users_username")),
    )
    op.create_table(
        "user_contact_channels",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("contact_value", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "channel_type",
            postgresql.ENUM("EMAIL", "TELEGRAM", name="contactchanneltype"),
            nullable=False,
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_user_contact_channels_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_contact_channels")),
        sa.UniqueConstraint(
            "user_id",
            "channel_type",
            "contact_value",
            name="unique_user_channel_contact",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("user_contact_channels")
    sa.Enum("EMAIL", "TELEGRAM", name="contactchanneltype").drop(op.get_bind())
    op.drop_table("users")
