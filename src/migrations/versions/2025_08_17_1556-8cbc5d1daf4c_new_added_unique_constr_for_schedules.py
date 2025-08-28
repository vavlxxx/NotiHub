"""new: added unique constr for schedules

Revision ID: 8cbc5d1daf4c
Revises: 01f3a975be62
Create Date: 2025-08-17 15:56:42.201615

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "8cbc5d1daf4c"
down_revision: Union[str, Sequence[str], None] = "01f3a975be62"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
        "unique_schedules",
        "notification_schedules",
        [
            "channel_id",
            "message",
            "schedule_type",
            "crontab",
            "max_executions",
        ],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("unique_schedules", "notification_schedules", type_="unique")
