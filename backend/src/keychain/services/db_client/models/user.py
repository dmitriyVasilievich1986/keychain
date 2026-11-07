"""User model for the database."""

__all__ = ("User",)

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from keychain.services.cryptography.client import CryptographyClient

from .base import Base

if TYPE_CHECKING:
    from .password import Password


class User(Base):
    """User model representing a user in the database.

    This model stores user authentication information including their name,
    password hash, creation timestamp, and the key material protecting the
    user's encrypted data. It also maintains a relationship with associated
    password records.

    Attributes:
        id: The unique identifier for the user.
        name: The name of the user.
        password_hash: The hashed password stored securely in the database.
        created_at: The timestamp when the user was created.
        encryption_salt: The random salt used to derive the user's key
            encryption key from their password. None for users created before
            per-user keys were introduced.
        wrapped_dek: The user's data encryption key, encrypted with the key
            derived from their password. None for users created before
            per-user keys were introduced.
        passwords: A list of password records associated with this user.

    """

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    encryption_salt: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    wrapped_dek: Mapped[str | None] = mapped_column(String, nullable=True)

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

    def unwrap_dek(self, password: str) -> bytes:
        """Recover the user's data encryption key using their password.

        Args:
            password: The user's plaintext password.

        Returns:
            The plaintext data encryption key.

        Raises:
            ValueError: If the user has no encryption keys yet.
            cryptography.fernet.InvalidToken: If the password is incorrect.

        """
        if self.encryption_salt is None or self.wrapped_dek is None:
            raise ValueError("User has no encryption keys")

        return CryptographyClient().unwrap_dek(password, self.encryption_salt, self.wrapped_dek)

    def __init__(self, name: str, password: str) -> None:
        """Initialize a new User instance.

        Creates a new user with the provided name and password. The password
        is immediately hashed using werkzeug's password hashing before being
        stored in the password_hash attribute, and a new data encryption key
        wrapped with the password is generated for the user.

        Args:
            name: The name of the user.
            password: The plaintext password that will be hashed and stored.

        """
        self.name = name
        self.password_hash = generate_password_hash(password)

        keys = CryptographyClient().create_user_keys(password)
        self.encryption_salt = keys.salt
        self.wrapped_dek = keys.wrapped_dek
