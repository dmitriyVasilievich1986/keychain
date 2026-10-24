"""Field value model."""

from datetime import datetime, timezone
from typing import Self

from pydantic import Field

from keychain.services.cryptography.client import CryptographyClient

from .base import BaseFirestoreSchema


class FieldValue(BaseFirestoreSchema):
    """Field value model."""

    value: str = Field(..., description="The value of the field.")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="The timestamp when the field value was created.",
    )

    def encrypt(self, cryptography_client: CryptographyClient | None = None) -> Self:
        """Encrypt the field value.

        Args:
            cryptography_client (CryptographyClient | None): Client used for
                encryption; a new :class:`CryptographyClient` is created if None.

        Returns:
            Self: A copy of the field value with ``value`` encrypted.

        """
        client = cryptography_client or CryptographyClient()
        return self.model_copy(update={"value": client.encrypt(self.value)})

    def decrypt(self, cryptography_client: CryptographyClient | None = None) -> Self:
        """Decrypt the field value.

        Args:
            cryptography_client (CryptographyClient | None): Client used for
                decryption; a new :class:`CryptographyClient` is created if None.

        Returns:
            Self: A copy of the field value with ``value`` decrypted.

        Raises:
            cryptography.fernet.InvalidToken: If ``value`` is invalid or was
                encrypted with a different key.

        """
        client = cryptography_client or CryptographyClient()
        return self.model_copy(update={"value": client.decrypt(self.value)})
