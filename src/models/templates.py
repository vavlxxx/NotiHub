from datetime import datetime
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import DateTime, ForeignKey, Text, UniqueConstraint, func
from src.models.base import Base


class Category(Base):
    title: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None]
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("template_categories.id"))

    templates: Mapped[list["Template"]] = relationship(back_populates="category")
    __tablename__ = "template_categories"


class Template(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str]
    content: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None]
    category_id: Mapped[int] = mapped_column(ForeignKey("template_categories.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default= func.now(), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default= func.now(), onupdate=func.now())
    category: Mapped["Category"] = relationship(back_populates="templates")
    
    __tablename__ = "templates"
    __table_args__ = (
        UniqueConstraint("user_id", "content", name="unique_templates_for_owner"),
    )
