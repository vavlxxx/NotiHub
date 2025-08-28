"""fix: provided DB security by adding extra fields and constraints

Revision ID: 0499d23fcf60
Revises: 2ea4271607d6
Create Date: 2025-08-13 11:37:24.893871

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0499d23fcf60"
down_revision: Union[str, Sequence[str], None] = "2ea4271607d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("templates", sa.Column("owner_id", sa.Integer(), nullable=False))
    op.create_unique_constraint(
        "unique_templates_for_owner", "templates", ["owner_id", "content"]
    )
    op.create_foreign_key(
        op.f("fk_templates_owner_id_users"),
        "templates",
        "users",
        ["owner_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        op.f("fk_templates_owner_id_users"), "templates", type_="foreignkey"
    )
    op.drop_constraint("unique_templates_for_owner", "templates", type_="unique")
    op.drop_column("templates", "owner_id")
