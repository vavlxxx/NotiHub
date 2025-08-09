from datetime import datetime
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import DateTime, ForeignKey, func
from src.models.base import Base


class Category(Base):
    title: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None]
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("template_categories.id"))

    templates: Mapped[list["Template"]] = relationship(back_populates="category")
    __tablename__ = "template_categories"


class Template(Base):
    title: Mapped[str]
    content: Mapped[str]
    description: Mapped[str | None]
    category_id: Mapped[int] = mapped_column(ForeignKey("template_categories.id"))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default= func.now(), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default= func.now(), onupdate=func.now())
    
    category: Mapped["Category"] = relationship(back_populates="templates")
    __tablename__ = "templates"
