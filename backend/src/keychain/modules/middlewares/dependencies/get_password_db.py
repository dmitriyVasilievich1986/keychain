"""Dependency provider for the passwords Firestore database."""

__all__ = ("get_password_db",)

from keychain.services.db_client.firestore import PasswordsFirestoreClient


def get_password_db() -> PasswordsFirestoreClient:
    """Provide the singleton Firestore client for the passwords database.

    The client is created with the passwords database config in the
    application lifespan, so this only returns the existing instance.

    Returns:
        PasswordsFirestoreClient: Client bound to the passwords database and
            collection.

    """
    return PasswordsFirestoreClient()
