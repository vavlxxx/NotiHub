from datetime import datetime
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, UniqueConstraint, func
from src.models.base import Base


class TemplateCategory(Base):
    name: Mapped[str]
    description: Mapped[str | None] = mapped_column(default=None)

    __tablename__ = "template_categories"


class Template(Base):
    title: Mapped[str] = mapped_column(unique=True)
    content: Mapped[str]
    category: Mapped[int] = mapped_column(ForeignKey("template_categories.id"))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    __tablename__ = "templates"


class TemplateVariable(Base):
    template_id: Mapped[int] = mapped_column(ForeignKey("templates.id"))
    name: Mapped[str]
    value: Mapped[str | None] = mapped_column(default=None)
    default_value: Mapped[str | None] = mapped_column(default=None) 
    description: Mapped[str | None] = mapped_column(default=None)

    __tablename__ = "template_variables"
    __table_args__ = (
        UniqueConstraint("template_id", "name", name="template_variable_unique"),
        CheckConstraint("value IS NOT NULL OR default_value IS NOT NULL", name="template_variable_initialized"),
    )
