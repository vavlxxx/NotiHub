"""refactor: removed and altered some useless fields

Revision ID: 2ea4271607d6
Revises: adfe32eca6d9
Create Date: 2025-08-13 08:45:56.582972

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2ea4271607d6"
down_revision: Union[str, Sequence[str], None] = "adfe32eca6d9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column("notification_logs", "processing_time_ms")
    op.alter_column(
        "notification_schedules",
        "max_executions",
        existing_type=sa.INTEGER(),
        nullable=False,
        existing_comment="Максимальное количество выполнений",
    )
    op.alter_column(
        "templates",
        "content",
        existing_type=sa.VARCHAR(),
        type_=sa.Text(),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "templates",
        "content",
        existing_type=sa.Text(),
        type_=sa.VARCHAR(),
        existing_nullable=False,
    )
    op.alter_column(
        "notification_schedules",
        "max_executions",
        existing_type=sa.INTEGER(),
        nullable=True,
        existing_comment="Максимальное количество выполнений",
    )
    op.add_column(
        "notification_logs",
        sa.Column(
            "processing_time_ms",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
            comment="Время обработки в миллисекундах",
        ),
    )
