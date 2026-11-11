"""Dependency provider for the users Firestore database."""

__all__ = ("get_users_db",)

from keychain.services.db_client.firestore import UsersFirestoreClient


def get_users_db() -> UsersFirestoreClient:
    """Provide the singleton Firestore client for the users database.

    The client is created with the users database config in the application
    lifespan, so this only returns the existing instance.

    Returns:
        UsersFirestoreClient: Client bound to the users database and collection.

    """
    return UsersFirestoreClient()
