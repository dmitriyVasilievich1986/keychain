"""User keys model."""

__all__ = ("UserKeys",)

from pydantic import BaseModel, Field

class UserKeys(BaseModel):
    """Key material generated for a user.

    Attributes:
        salt: The random salt used to derive the user's key encryption key.
        wrapped_dek: The user's data encryption key, encrypted with the key
            encryption key. Safe to store in the database.
        dek: The plaintext data encryption key. Must never be persisted.

    """

    salt: bytes = Field(..., description="The random salt used to derive the user's key encryption key")
    wrapped_dek: str = Field(..., description="The user's data encryption key, encrypted with the key encryption key. Safe to store in the database")
    dek: bytes = Field(..., description="The plaintext data encryption key. Must never be persisted")