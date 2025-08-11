"""new: Schedule and Notification Log models

Revision ID: 3d10416a9956
Revises: a36645894a72
Create Date: 2025-08-11 12:17:06.798688

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "3d10416a9956"
down_revision: Union[str, Sequence[str], None] = "a36645894a72"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("DROP TYPE IF EXISTS notificationstatus")
    op.create_table(
        "notification_logs",
        sa.Column("contact_data", sa.String(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column(
            "provider_name",
            postgresql.ENUM("EMAIL", "TELEGRAM", name="contactchanneltype", create_type=False),
            nullable=False,
        ),
        sa.Column(
            "provider_response",
            sa.String(),
            nullable=True,
            comment="Ответ от провайдера",
        ),
        sa.Column(
            "status",
            postgresql.ENUM("SUCCESS", "FAILURE", "PENDING", name="notificationstatus"),
            nullable=False,
        ),
        sa.Column(
            "delivered_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "processing_time_ms",
            sa.Integer(),
            nullable=True,
            comment="Время обработки в миллисекундах",
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_notification_logs")),
    )
    op.create_table(
        "notification_schedules",
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=False),
        sa.Column("schedule_type", sa.String(length=20), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "crontab",
            sa.String(length=100),
            nullable=True,
            comment="Cron выражение: минута час день месяц день_недели",
        ),
        sa.Column(
            "max_executions",
            sa.Integer(),
            nullable=True,
            comment="Максимальное количество выполнений (для recurring)",
        ),
        sa.Column(
            "current_executions",
            sa.Integer(),
            nullable=False,
            comment="Текущее количество выполнений",
        ),
        sa.Column(
            "last_executed_at", sa.DateTime(timezone=True), nullable=True
        ),
        sa.Column(
            "next_execution_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Следующее время выполнения (вычисляется автоматически)",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "(schedule_type = 'ONCE' AND scheduled_at IS NOT NULL) OR schedule_type != 'ONCE'",
            name=op.f("ck_notification_schedules_once_requires_scheduled_at"),
        ),
        sa.CheckConstraint(
            "(schedule_type = 'RECURRING' AND crontab IS NOT NULL) OR schedule_type != 'RECURRING'",
            name=op.f("ck_notification_schedules_recurring_requires_cron"),
        ),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["user_contact_channels.id"],
            name=op.f(
                "fk_notification_schedules_channel_id_user_contact_channels"
            ),
            onupdate="restrict",
            ondelete="restrict",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_notification_schedules")),
    )
    op.drop_column("users", "notification_enabled")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "users",
        sa.Column(
            "notification_enabled",
            sa.BOOLEAN(),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.drop_table("notification_schedules")
    op.drop_table("notification_logs")
    op.execute("DROP TYPE IF EXISTS notificationstatus")