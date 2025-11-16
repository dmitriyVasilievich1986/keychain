"""Password model for the database."""

__all__ = ["Password"]

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .field import Field
    from .user import User


class Password(Base):
    """Password model representing a password in the database.

    This model stores password information including its name, creation timestamp,
    and image URL. It also maintains relationships with the user who owns the password
    and the fields associated with the password.

    Attributes:
        id: The unique identifier for the password.
        name: The name of the password.
        created_at: The timestamp when the password was created.
        image_url: The URL of the image associated with the password.
        user_id: The unique identifier for the user who owns the password.
        user: The user who owns the password.
        fields: A list of fields associated with the password.

    """

    __tablename__ = "password"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    image_url: Mapped[str | None] = mapped_column(String, nullable=True, default="/static/i/no-photo.png")

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="passwords")

    fields: Mapped[list["Field"]] = relationship("Field", back_populates="password")
