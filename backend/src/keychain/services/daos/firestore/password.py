"""Firestore data access object for password documents."""

__all__ = ("PasswordDAO",)


from .base import BaseFirestoreDAO
from .models import Password


class PasswordDAO(BaseFirestoreDAO[Password]):
    """Provide Firestore access operations for :class:`Password` documents.

    New documents get a random UUID4 as their document ID.
    """

    id_field: str = "id"
    document_model: type[Password] = Password
