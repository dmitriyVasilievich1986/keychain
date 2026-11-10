"""Firestore password model."""

from datetime import datetime, timezone
from typing import Self
from uuid import uuid4

from pydantic import Field

from keychain.services.cryptography.client import CryptographyClient

from .base import BaseFirestoreSchema
from .field import Field as FieldModel


class Password(BaseFirestoreSchema):
    """Password document stored in Firestore.

    A password belongs to a single user and embeds its fields, each of which
    keeps the history of its values. Deletion is soft: ``deleted_at`` is set
    instead of removing the document.

    Attributes:
        id (str): The ID of the password; a random UUID4 by default.
        name (str): The name of the password.
        description (str | None): The description of the password.
        user_id (str): The ID of the user who owns the password.
        image_url (str | None): The URL of the password image.
        fields (list[FieldModel]): The fields embedded in the password.
        created_at (datetime): The UTC timestamp when the password was created.
        updated_at (datetime): The UTC timestamp when the password was last updated.
        deleted_at (datetime | None): The UTC timestamp when the password was
            deleted, or None if it is not deleted.

    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="The ID of the password.")
    name: str = Field(..., description="The name of the password.")
    description: str | None = Field(default=None, description="The description of the password.")
    user_id: str = Field(..., description="The ID of the user who owns the password.")
    image_url: str | None = Field(default=None, description="The URL of the password image.")
    fields: list[FieldModel] = Field(..., description="The fields of the password.")

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="The timestamp when the password was created."
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="The timestamp when the password was last updated.",
    )
    deleted_at: datetime | None = Field(default=None, description="The timestamp when the password was deleted.")

    def set_deleted(self) -> None:
        """Mark the password as deleted by setting ``deleted_at`` to the current UTC time.

        Only the model instance is changed; persist it through the DAO to
        store the deletion.

        Returns:
            None

        """
        self.deleted_at = datetime.now(timezone.utc)

    def encrypt(self, dek: bytes, cryptography_client: CryptographyClient | None = None) -> Self:
        """Encrypt the values of all fields of the password.

        Args:
            dek (bytes): The owner's data encryption key.
            cryptography_client (CryptographyClient | None): Client used for
                encryption; a new :class:`CryptographyClient` is created if None.

        Returns:
            Self: A copy of the password with every field value encrypted.

        """
        client = cryptography_client or CryptographyClient()
        fields = [field.encrypt(dek, client) for field in self.fields]
        return self.model_copy(update={"fields": fields})

    def decrypt(self, dek: bytes, cryptography_client: CryptographyClient | None = None) -> Self:
        """Decrypt the values of all fields of the password.

        Args:
            dek (bytes): The owner's data encryption key.
            cryptography_client (CryptographyClient | None): Client used for
                decryption; a new :class:`CryptographyClient` is created if None.

        Returns:
            Self: A copy of the password with every field value decrypted.

        Raises:
            cryptography.fernet.InvalidToken: If any field value is invalid or was
                encrypted with a different key.

        """
        client = cryptography_client or CryptographyClient()
        fields = [field.decrypt(dek, client) for field in self.fields]
        return self.model_copy(update={"fields": fields})
