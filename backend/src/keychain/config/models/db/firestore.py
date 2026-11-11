"""Firestore database configuration settings."""

__all__ = ("FirestoreConfig",)

from pydantic import BaseModel, Field


class FirestoreConfig(BaseModel):
    """Firestore database configuration model.

    This model stores the Firestore database configuration settings including the database
    name and collection name.

    Attributes:
        db_name: The name of the database.
        collection_name: The name of the collection.

    """

    db_name: str = Field(..., description="The name of the table")
    collection_name: str = Field(..., description="The name of the collection")
