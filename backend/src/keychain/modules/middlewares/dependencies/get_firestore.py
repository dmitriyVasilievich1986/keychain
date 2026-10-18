"""Dependency provider for Firestore client."""

__all__ = ["get_firestore"]

from keychain.services.db_client.firestore import FirestoreClient


def get_firestore() -> FirestoreClient:
    """Dependency function that provides a singleton instance of FirestoreClient."""
    return FirestoreClient()
