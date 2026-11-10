"""Database configuration settings."""

__all__ = ("DBConfig",)

from pydantic import BaseModel, Field

from .firestore import FirestoreConfig


class DBConfig(BaseModel):
    """Database configuration model.

    This model stores the Firestore databases and collections used by the
    application.

    Attributes:
        firestore: Firestore configuration for password documents.
        users: Firestore configuration for user documents.

    """

    firestore: FirestoreConfig = Field(..., description="Firestore configuration for password documents")
    users: FirestoreConfig = Field(..., description="Firestore configuration for user documents")
