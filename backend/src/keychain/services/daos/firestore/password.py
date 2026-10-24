"""Firestore data access object for password documents."""

__all__ = ("PasswordDAO",)


from typing import Any

from google.cloud.firestore import DocumentSnapshot

from .base import BaseFirestoreDAO
from .models import Password


class PasswordDAO(BaseFirestoreDAO[Password]):
    """Provide Firestore access operations for :class:`Password` documents.

    New documents get a random UUID4 as their document ID.
    """

    id_field: str = "id"
    document_model: type[Password] = Password

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

    def to_document(self, model: Password) -> dict[str, Any]:
        """Serialize a password into a Firestore document body with encrypted field values.

        Args:
            model (Password): Password to store.

        Returns:
            dict[str, Any]: Document body without :attr:`id_field`.

        """
        return super().to_document(model.encrypt())
