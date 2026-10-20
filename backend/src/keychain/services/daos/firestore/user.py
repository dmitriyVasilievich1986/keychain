"""Firestore data access object for user documents."""

__all__ = ("UserDAO",)

from datetime import datetime, timezone
from typing import Any

from google.api_core.exceptions import NotFound
from google.cloud.firestore_v1.base_query import FieldFilter
from werkzeug.security import generate_password_hash

from .base import BaseFirestoreDAO
from .models import User


class UserDAO(BaseFirestoreDAO[User]):
    """Provide Firestore access operations for :class:`User` documents.

    Users live in the ``users`` collection by default, and new documents get
    a random UUID4 as their document ID.
    """

    id_field: str = "id"
    document_model: type[User] = User
    collection_name: str | None = "users"

    async def create(self, **kwargs: Any) -> User:
        """Validate and insert a new user document.

        A plaintext ``password`` in ``kwargs`` is hashed and stored as
        ``password_hash``.

        Args:
            **kwargs (Any): Field values for the new model.

        Returns:
            User: The stored user.

        Raises:
            Conflict: If a document with ``document_id`` already exists.

        """
        if (password := kwargs.pop("password", None)) is None:
            raise ValueError("Password is required")

        kwargs["password_hash"] = generate_password_hash(password)
        return await super().create(**kwargs)

    async def get_by_username(self, username: str) -> User:
        """Load a user by their username.

        Args:
            username (str): The username to look up (matched against
                ``name``).

        Returns:
            User: The matching user.

        Raises:
            NotFound: If no user has this username.

        """
        snapshots = await self._build_query([FieldFilter("name", "==", username)]).limit(1).get()
        if not snapshots:
            raise NotFound(f"User {username!r} not found in {self.collection.id!r}")
        return self.to_model(snapshots[0])

    async def reset_password(self, document_id: str, password: str) -> User:
        """Hash and store a new password for a user.

        Args:
            document_id (str): Document ID of the user.
            password (str): The new plaintext password.

        Returns:
            User: The updated user.

        Raises:
            NotFound: If the user does not exist.

        """
        return await self.update(
            document_id,
            password_hash=generate_password_hash(password),
            updated_at=datetime.now(timezone.utc),
        )
