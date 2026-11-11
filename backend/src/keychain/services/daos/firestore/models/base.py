"""Base Firestore model."""

__all__ = ("BaseFirestoreSchema",)

from pydantic import BaseModel, ConfigDict


class BaseFirestoreSchema(BaseModel):
    """Base schema for all Firestore models."""

    model_config = ConfigDict(
        validate_assignment=True,
        serialize_by_alias=False,
        validate_by_alias=False,
    )
