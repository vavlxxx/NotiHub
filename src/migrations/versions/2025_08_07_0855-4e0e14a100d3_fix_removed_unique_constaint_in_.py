"""fix: removed unique constaint in Templates model

Revision ID: 4e0e14a100d3
Revises: 99b29d44e46a
Create Date: 2025-08-07 08:55:18.442381

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "4e0e14a100d3"
down_revision: Union[str, Sequence[str], None] = "99b29d44e46a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(op.f("uq_templates_title"), "templates", type_="unique")


def downgrade() -> None:
    """Downgrade schema."""
    op.create_unique_constraint(
        op.f("uq_templates_title"),
        "templates",
        ["title"],
        postgresql_nulls_not_distinct=False,
    )
