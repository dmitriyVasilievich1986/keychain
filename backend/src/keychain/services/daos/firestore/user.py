"""Firestore data access object for user documents."""

__all__ = ("UserDAO",)

from datetime import datetime, timezone
from typing import Any

from google.api_core.exceptions import NotFound
from google.cloud.firestore_v1.base_query import FieldFilter
from werkzeug.security import generate_password_hash

from keychain.services.cryptography.client import CryptographyClient
from keychain.services.daos.exceptions import EncryptionKeysMissingError, InvalidPasswordError

from .base import BaseFirestoreDAO
from .models import User
from .password import PasswordDAO


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
        ``password_hash``, and a new data encryption key wrapped with the
        password is generated for the user.

        Args:
            **kwargs (Any): Field values for the new model.

        Returns:
            User: The stored user.

        Raises:
            ValueError: If ``password`` is not provided.
            Conflict: If a document with ``document_id`` already exists.

        """
        if (password := kwargs.pop("password", None)) is None:
            raise ValueError("Password is required")

        keys = CryptographyClient().create_user_keys(password)
        kwargs["password_hash"] = generate_password_hash(password)
        kwargs["encryption_salt"] = keys.salt
        kwargs["wrapped_dek"] = keys.wrapped_dek
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

    async def reset_password(self, document_id: str, old_password: str, new_password: str) -> User:
        """Change a user's password while keeping their data readable.

        The user's data encryption key is unwrapped with the old password and
        wrapped again with the new one, so every field value the user owns
        stays decryptable without being re-encrypted.

        Args:
            document_id (str): Document ID of the user.
            old_password (str): The user's current plaintext password.
            new_password (str): The new plaintext password.

        Returns:
            User: The updated user.

        Raises:
            NotFound: If the user does not exist.
            InvalidPasswordError: If ``old_password`` is incorrect.
            EncryptionKeysMissingError: If the user has not been migrated to
                per-user encryption yet.

        """
        user = await self.get_by_id(document_id)
        if not user.verify_password(old_password):
            raise InvalidPasswordError("Invalid password")

        if user.encryption_salt is None or user.wrapped_dek is None:
            raise EncryptionKeysMissingError(f"User {user.id} has no encryption keys, migrate the user first")

        keys = CryptographyClient().rewrap_dek(old_password, new_password, user.encryption_salt, user.wrapped_dek)
        return await self.update(
            document_id,
            password_hash=generate_password_hash(new_password),
            encryption_salt=keys.salt,
            wrapped_dek=keys.wrapped_dek,
        )

    async def force_reset_password(self, document_id: str, new_password: str, password_dao: PasswordDAO) -> User:
        """Reset a user's password without knowing the current one.

        Without the current password the user's data encryption key cannot be
        recovered, so the fields of all of the user's passwords are permanently
        deleted and a new key is generated. Password documents themselves are
        kept. All changes are written atomically in one batch.

        Args:
            document_id (str): Document ID of the user.
            new_password (str): The new plaintext password.
            password_dao (PasswordDAO): DAO for the collection holding the
                user's passwords.

        Returns:
            User: The updated user.

        Raises:
            NotFound: If the user does not exist.

        """
        user = await self.get_by_id(document_id)
        keys = CryptographyClient().create_user_keys(new_password)
        now = datetime.now(timezone.utc)

        batch = self.firestore_client.client.batch()
        passwords = await password_dao.collection.where(filter=FieldFilter("user_id", "==", user.id)).get()
        for snapshot in passwords:
            batch.update(snapshot.reference, {"fields": [], "updated_at": now})

        batch.update(
            self.collection.document(document_id),
            {
                "password_hash": generate_password_hash(new_password),
                "encryption_salt": keys.salt,
                "wrapped_dek": keys.wrapped_dek,
                "updated_at": now,
            },
        )
        await batch.commit()

        return await self.get_by_id(document_id)
