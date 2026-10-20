"""Field value model."""

from datetime import datetime, timezone

from pydantic import Field

from .base import BaseFirestoreSchema


class FieldValue(BaseFirestoreSchema):
    """Field value model."""

    value: str = Field(..., description="The value of the field.")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="The timestamp when the field value was created.",
    )
