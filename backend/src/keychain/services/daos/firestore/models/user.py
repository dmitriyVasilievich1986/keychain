"""Firestore user model."""

__all__ = ("User",)

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import Field
from werkzeug.security import check_password_hash

from .base import BaseFirestoreSchema


class User(BaseFirestoreSchema):
    """User model."""

    id: str = Field(default_factory=lambda: str(uuid4()), description="The ID of the user.")
    name: str = Field(..., description="The name of the user.")
    password_hash: str = Field(..., description="The hashed password of the user.")

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="The timestamp when the user was created."
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="The timestamp when the user was last updated."
    )

    def verify_password(self, password: str) -> bool:
        """Check a plaintext password against the stored hash.

        Args:
            password (str): The plaintext password to verify.

        Returns:
            bool: True if the password matches the stored hash.

        """
        return check_password_hash(self.password_hash, password)
