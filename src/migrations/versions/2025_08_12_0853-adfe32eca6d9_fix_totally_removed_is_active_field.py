"""fix: totally removed 'is_active field'

Revision ID: adfe32eca6d9
Revises: 3d10416a9956
Create Date: 2025-08-12 08:53:36.749682

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "adfe32eca6d9"
down_revision: Union[str, Sequence[str], None] = "3d10416a9956"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "notification_schedules",
        "max_executions",
        existing_type=sa.INTEGER(),
        nullable=False,
        comment="Максимальное количество выполнений",
        existing_comment="Максимальное количество выполнений (для recurring)",
    )
    op.drop_column("templates", "is_active")
    op.drop_column("user_contact_channels", "is_active")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "user_contact_channels",
        sa.Column("is_active", sa.BOOLEAN(), autoincrement=False, nullable=False),
    )
    op.add_column(
        "templates",
        sa.Column("is_active", sa.BOOLEAN(), autoincrement=False, nullable=False),
    )
    op.alter_column(
        "notification_schedules",
        "max_executions",
        existing_type=sa.INTEGER(),
        nullable=True,
        comment="Максимальное количество выполнений (для recurring)",
        existing_comment="Максимальное количество выполнений",
    )
