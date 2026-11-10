"""Firestore user model."""

__all__ = ("User",)

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import Field
from werkzeug.security import check_password_hash

from keychain.services.cryptography.client import CryptographyClient

from .base import BaseFirestoreSchema


class User(BaseFirestoreSchema):
    """User document stored in Firestore.

    Besides the authentication data, a user holds the key material that
    protects their encrypted field values: a random data encryption key (DEK)
    wrapped with a key derived from the user's password.

    Attributes:
        id (str): The ID of the user; a random UUID4 by default.
        name (str): The name of the user.
        password_hash (str): The hashed password of the user.
        encryption_salt (bytes | None): The random salt used to derive the
            user's key encryption key. None for users created before per-user
            keys were introduced.
        wrapped_dek (str | None): The user's data encryption key, encrypted
            with the key derived from their password. None for users created
            before per-user keys were introduced.
        created_at (datetime): The UTC timestamp when the user was created.
        updated_at (datetime): The UTC timestamp when the user was last updated.

    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="The ID of the user.")
    name: str = Field(..., description="The name of the user.")
    password_hash: str = Field(..., description="The hashed password of the user.")
    encryption_salt: bytes | None = Field(
        default=None, description="The random salt used to derive the user's key encryption key."
    )
    wrapped_dek: str | None = Field(
        default=None, description="The user's data encryption key, wrapped with their password."
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="The timestamp when the user was created."
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="The timestamp when the user was last updated."
    )

    @property
    def has_encryption_keys(self) -> bool:
        """Whether the user has per-user encryption keys.

        Returns:
            bool: True if both the salt and the wrapped key are set.

        """
        return self.encryption_salt is not None and self.wrapped_dek is not None

    def verify_password(self, password: str) -> bool:
        """Check a plaintext password against the stored hash.

        Args:
            password (str): The plaintext password to verify.

        Returns:
            bool: True if the password matches the stored hash.

        """
        return check_password_hash(self.password_hash, password)

    def unwrap_dek(self, password: str) -> bytes:
        """Recover the user's data encryption key using their password.

        Args:
            password (str): The user's plaintext password.

        Returns:
            bytes: The plaintext data encryption key.

        Raises:
            ValueError: If the user has no encryption keys yet.
            cryptography.fernet.InvalidToken: If the password is incorrect.

        """
        if self.encryption_salt is None or self.wrapped_dek is None:
            raise ValueError("User has no encryption keys")

        return CryptographyClient().unwrap_dek(password, self.encryption_salt, self.wrapped_dek)
