"""Firestore data access object for password documents."""

__all__ = ("PasswordDAO",)


from datetime import datetime, timezone
from typing import Any, override

from google.cloud.firestore import DocumentSnapshot

from .base import BaseFirestoreDAO
from .models import Password


class PasswordDAO(BaseFirestoreDAO[Password]):
    """Provide Firestore access operations for :class:`Password` documents.

    New documents get a random UUID4 as their document ID.
    """

    id_field: str = "id"
    document_model: type[Password] = Password

    @override
    def to_model(self, snapshot: DocumentSnapshot) -> Password:
        """Build a password model from a document snapshot and decrypt its field values.

        Args:
            snapshot (DocumentSnapshot): An existing password document.

        Returns:
            Password: Password with the document ID set on :attr:`id_field`
                and decrypted field values.

        Raises:
            cryptography.fernet.InvalidToken: If any stored field value is
                invalid or was encrypted with a different key.

        """
        return super().to_model(snapshot).decrypt()

    @override
    def to_document(self, model: Password) -> dict[str, Any]:
        """Serialize a password into a Firestore document body with encrypted field values.

        Args:
            model (Password): Password to store.

        Returns:
            dict[str, Any]: Document body without :attr:`id_field`.

        """
        return super().to_document(model.encrypt())

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
