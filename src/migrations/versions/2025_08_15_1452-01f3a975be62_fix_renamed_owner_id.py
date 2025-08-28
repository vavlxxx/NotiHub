"""fix: renamed owner_id

Revision ID: 01f3a975be62
Revises: 0499d23fcf60
Create Date: 2025-08-15 14:52:01.468460

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "01f3a975be62"
down_revision: Union[str, Sequence[str], None] = "0499d23fcf60"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("templates", sa.Column("user_id", sa.Integer(), nullable=False))
    op.drop_constraint(op.f("unique_templates_for_owner"), "templates", type_="unique")
    op.create_unique_constraint(
        "unique_templates_for_owner", "templates", ["user_id", "content"]
    )
    op.drop_constraint(
        op.f("fk_templates_owner_id_users"), "templates", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("fk_templates_user_id_users"),
        "templates",
        "users",
        ["user_id"],
        ["id"],
    )
    op.drop_column("templates", "owner_id")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "templates",
        sa.Column("owner_id", sa.INTEGER(), autoincrement=False, nullable=False),
    )
    op.drop_constraint(
        op.f("fk_templates_user_id_users"), "templates", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("fk_templates_owner_id_users"),
        "templates",
        "users",
        ["owner_id"],
        ["id"],
    )
    op.drop_constraint("unique_templates_for_owner", "templates", type_="unique")
    op.create_unique_constraint(
        op.f("unique_templates_for_owner"),
        "templates",
        ["owner_id", "content"],
        postgresql_nulls_not_distinct=False,
    )
    op.drop_column("templates", "user_id")
