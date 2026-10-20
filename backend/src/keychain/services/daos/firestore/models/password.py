"""Firestore password model."""

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import Field

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
