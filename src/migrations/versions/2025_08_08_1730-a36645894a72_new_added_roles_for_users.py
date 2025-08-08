"""new: added roles for users

Revision ID: a36645894a72
Revises: e933f7a200d0
Create Date: 2025-08-08 17:30:35.101830

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a36645894a72"
down_revision: Union[str, Sequence[str], None] = "e933f7a200d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("DROP TYPE IF EXISTS userrole")
    user_role_enum = postgresql.ENUM("ADMIN", "USER", name="userrole")
    user_role_enum.create(op.get_bind())

    op.add_column(
        "users",
        sa.Column(
            "role",
            user_role_enum,
            server_default="USER",
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "role")
    op.execute("DROP TYPE IF EXISTS userrole")
