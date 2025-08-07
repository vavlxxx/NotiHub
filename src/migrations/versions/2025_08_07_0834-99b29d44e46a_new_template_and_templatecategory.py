"""new: Template and TemplateCategory

Revision ID: 99b29d44e46a
Revises:
Create Date: 2025-08-07 08:34:30.957099

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "99b29d44e46a"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "template_categories",
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["template_categories.id"],
            name=op.f("fk_template_categories_parent_id_template_categories"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_template_categories")),
        sa.UniqueConstraint(
            "title", name=op.f("uq_template_categories_title")
        ),
    )
    op.create_table(
        "templates",
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["template_categories.id"],
            name=op.f("fk_templates_category_id_template_categories"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_templates")),
        sa.UniqueConstraint("title", name=op.f("uq_templates_title")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("templates")
    op.drop_table("template_categories")
