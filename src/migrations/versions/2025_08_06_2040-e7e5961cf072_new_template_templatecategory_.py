"""new: Template, TemplateCategory, TemplateVariable

Revision ID: e7e5961cf072
Revises:
Create Date: 2025-08-06 20:40:11.638427

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e7e5961cf072"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "template_categories",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_template_categories")),
    )
    op.create_table(
        "templates",
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("category", sa.Integer(), nullable=False),
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
            ["category"],
            ["template_categories.id"],
            name=op.f("fk_templates_category_template_categories"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_templates")),
        sa.UniqueConstraint("title", name=op.f("uq_templates_title")),
    )
    op.create_table(
        "template_variables",
        sa.Column("template_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("value", sa.String(), nullable=True),
        sa.Column("default_value", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "value IS NOT NULL OR default_value IS NOT NULL",
            name=op.f("ck_template_variables_template_variable_initialized"),
        ),
        sa.ForeignKeyConstraint(
            ["template_id"],
            ["templates.id"],
            name=op.f("fk_template_variables_template_id_templates"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_template_variables")),
        sa.UniqueConstraint(
            "template_id", "name", name="template_variable_unique"
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("template_variables")
    op.drop_table("templates")
    op.drop_table("template_categories")
