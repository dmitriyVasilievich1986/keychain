"""Firestore data access object for password documents."""

__all__ = ("PasswordDAO",)


from datetime import datetime, timezone
from typing import Any, override

from google.cloud.firestore import DocumentSnapshot

from keychain.services.db_client.firestore import FirestoreClient

from .base import BaseFirestoreDAO
from .models import Password


class PasswordDAO(BaseFirestoreDAO[Password]):
    """Provide Firestore access operations for :class:`Password` documents.

    New documents get a random UUID4 as their document ID.

    Field values are encrypted with the owner's data encryption key (DEK).
    A DAO built with ``dek`` transparently decrypts values on read and
    encrypts them on write. Without ``dek`` the DAO works on the stored
    ciphertext as is, which is enough for listing, renaming or deleting
    passwords, but it refuses to write field values.
    """

    id_field: str = "id"
    document_model: type[Password] = Password

    def __init__(
        self,
        firestore_client: FirestoreClient,
        collection_name: str | None = None,
        *,
        dek: bytes | None = None,
        **kwargs: Any,
    ) -> None:
        """Bind the DAO to a Firestore client, a collection and an optional key.

        Args:
            firestore_client (FirestoreClient): Client that owns the
                underlying ``AsyncClient``.
            collection_name (str | None, optional): Collection this instance
                operates on; None keeps the class-level ``collection_name``.
                Defaults to None.
            dek (bytes | None, optional): The owner's data encryption key used
                to encrypt and decrypt field values. Defaults to None.
            **kwargs (Any): Extra arguments forwarded to the base DAO.

        """
        super().__init__(firestore_client, collection_name, **kwargs)
        self.dek = dek

    @override
    def to_model(self, snapshot: DocumentSnapshot) -> Password:
        """Build a password model from a document snapshot.

        Field values are decrypted when the DAO has a data encryption key.

        Args:
            snapshot (DocumentSnapshot): An existing password document.

        Returns:
            Password: Password with the document ID set on :attr:`id_field`.

        Raises:
            cryptography.fernet.InvalidToken: If any stored field value is
                invalid or was encrypted with a different key.

        """
        password = super().to_model(snapshot)
        return password if self.dek is None else password.decrypt(self.dek)

    @override
    def to_document(self, model: Password) -> dict[str, Any]:
        """Serialize a password into a Firestore document body.

        Field values are encrypted when the DAO has a data encryption key.

        Args:
            model (Password): Password to store.

        Returns:
            dict[str, Any]: Document body without :attr:`id_field`.

        """
        return super().to_document(model if self.dek is None else model.encrypt(self.dek))

    def _ensure_can_write_fields(self, kwargs: dict[str, Any]) -> None:
        """Refuse to write field values without a data encryption key.

        Args:
            kwargs (dict[str, Any]): Field values about to be written.

        Raises:
            ValueError: If ``fields`` is non-empty and the DAO has no key.

        """
        if self.dek is None and kwargs.get("fields"):
            raise ValueError("Data encryption key is required to write field values")

    @override
    async def create(self, **kwargs: Any) -> Password:
        """Validate and insert a new password document.

        Args:
            **kwargs (Any): Field values for the new password, with plaintext
                field values.

        Returns:
            Password: The stored password.

        Raises:
            ValueError: If field values are given but the DAO has no key.

        """
        self._ensure_can_write_fields(kwargs)
        return await super().create(**kwargs)

    @override
    async def update(self, document_id: str, **kwargs: Any) -> Password:
        """Validate and apply a partial update to one password document.

        Args:
            document_id (str): Document ID.
            **kwargs (Any): Field values to set, with plaintext field values.

        Returns:
            Password: The password after the update.

        Raises:
            NotFound: If the document does not exist.
            ValueError: If field values are given but the DAO has no key.

        """
        self._ensure_can_write_fields(kwargs)
        return await super().update(document_id, **kwargs)

    async def mark_as_deleted(self, document_id: str) -> bool:
        """Soft-delete one password by setting ``deleted_at``.

        The document is kept in Firestore; use :meth:`delete` to remove it.
        A password that is already deleted keeps its original ``deleted_at``.

        Args:
            document_id (str): Document ID.

        Returns:
            bool: Always ``True`` after the password is marked as deleted.

        Raises:
            NotFound: If the document does not exist.

        """
        password = await self.get_by_id(document_id)
        if password.deleted_at is None:
            await self.update(document_id, deleted_at=datetime.now(timezone.utc))
        return True
