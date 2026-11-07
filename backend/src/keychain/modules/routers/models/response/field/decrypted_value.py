"""Helpers for building field responses with decrypted values."""

__all__ = ("DecryptedValueMixin",)

from typing import Any

from pydantic import BaseModel, model_validator, ValidationInfo

from keychain.services.cryptography.client import CryptographyClient
from keychain.services.db_client.models.field import Field


class DecryptedValueMixin(BaseModel):
    """Mixin that fills ``value_decrypted`` from an ORM :class:`Field`.

    The owner's data encryption key must be passed in the validation context
    under the ``dek`` key, e.g. ``Model.model_validate(field, context={"dek": dek})``.
    The context is propagated to nested models as well.
    """

    @model_validator(mode="before")
    @classmethod
    def _decrypt_value(cls, data: Any, info: ValidationInfo) -> Any:
        """Replace an ORM field with a mapping that includes its decrypted value.

        Args:
            data (Any): The raw input being validated.
            info (ValidationInfo): The validation info carrying the context.

        Returns:
            Any: A mapping with ``value_decrypted`` for ORM fields, otherwise
                the unchanged input.

        Raises:
            ValueError: If no data encryption key is present in the context.

        """
        if not isinstance(data, Field):
            return data

        if not info.context or (dek := info.context.get("dek")) is None:
            raise ValueError("Data encryption key is required in the validation context")

        payload = {name: getattr(data, name) for name in cls.model_fields if name != "value_decrypted"}
        payload["value_decrypted"] = CryptographyClient().decrypt(data.value, dek)
        return payload
