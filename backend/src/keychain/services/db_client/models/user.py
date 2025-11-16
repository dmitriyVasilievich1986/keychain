"""User model for the database."""

__all__ = ["User"]

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from .base import Base

if TYPE_CHECKING:
    from .password import Password


class User(Base):
    """User model representing a user in the database.

    This model stores user authentication information including their name,
    password hash, and creation timestamp. It also maintains a relationship
    with associated password records.

    Attributes:
        id: The unique identifier for the user.
        name: The name of the user.
        password_hash: The hashed password stored securely in the database.
        created_at: The timestamp when the user was created.
        passwords: A list of password records associated with this user.

    """

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)

    passwords: Mapped[list["Password"]] = relationship("Password", back_populates="user")

    def verify_password(self, password: str) -> bool:
        """Verify if the provided password matches the user's stored password hash.

        This method uses werkzeug's password hashing to securely compare the
        provided plaintext password with the stored password hash.

        Args:
            password: The plaintext password to verify.

        Returns:
            True if the password matches the stored hash, False otherwise.

        """
        return check_password_hash(self.password_hash, password)

    def __init__(self, name: str, password: str) -> None:
        """Initialize a new User instance.

        Creates a new user with the provided name and password. The password
        is immediately hashed using werkzeug's password hashing before being
        stored in the password_hash attribute.

        Args:
            name: The name of the user.
            password: The plaintext password that will be hashed and stored.

        """
        self.name = name
        self.password_hash = generate_password_hash(password)
