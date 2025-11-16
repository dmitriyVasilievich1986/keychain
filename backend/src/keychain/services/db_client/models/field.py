"""Field model for the database."""

__all__ = ["Field"]

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .password import Password


class Field(Base):
    """Field model representing a field in the database.

    This model stores field information including its name, value, creation timestamp,
    and deletion status. It also maintains a relationship with the password that
    the field belongs to.

    Attributes:
        id: The unique identifier for the field.
        name: The name of the field.
        value: The value of the field.
        created_at: The timestamp when the field was created.
        updated_at: The timestamp when the field was last updated.
        is_deleted: Whether the field has been deleted.
        password_id: The unique identifier for the password that the field belongs to.
        password: The password that the field belongs to.

    """

    __tablename__ = "field"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    value: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    password_id: Mapped[int] = mapped_column(Integer, ForeignKey("password.id"), nullable=False)
    password: Mapped["Password"] = relationship("Password", back_populates="fields")
