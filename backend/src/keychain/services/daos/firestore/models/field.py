"""Firestore password field model."""

from datetime import datetime, timezone

from pydantic import Field

from .base import BaseFirestoreSchema
from .field_value import FieldValue


class Field(BaseFirestoreSchema):
    """Field embedded in a password document.

    A field keeps the full history of its values instead of overwriting them.
    Deletion is soft: ``deleted_at`` is set instead of removing the field.

    Attributes:
        name (str): The name of the field.
        position (int): The position of the field within the password.
        values (list[FieldValue]): The values of the field, in the order they
            were added.
        created_at (datetime): The UTC timestamp when the field was created.
        updated_at (datetime): The UTC timestamp when the field was last updated.
        deleted_at (datetime | None): The UTC timestamp when the field was
            deleted, or None if it is not deleted.

    """

    name: str = Field(..., description="The name of the field.")
    position: int = Field(..., description="The position of the field.")
    values: list[FieldValue] = Field(..., description="The values of the field.")

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="The timestamp when the field was created."
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="The timestamp when the field was last updated."
    )
    deleted_at: datetime | None = Field(default=None, description="The timestamp when the field was deleted.")

    def set_deleted(self) -> None:
        """Mark the field as deleted by setting ``deleted_at`` to the current UTC time.

        Only the model instance is changed; persist the owning password through
        the DAO to store the deletion.

        Returns:
            None

        """
        self.deleted_at = datetime.now(timezone.utc)
