"""Tests for the Firestore client against the emulator."""

import pytest

from keychain.services.db_client import FirestoreClient

pytestmark = pytest.mark.integration


async def test_healthcheck_succeeds(firestore_client: FirestoreClient) -> None:
    """A reachable Firestore emulator returns ``True``."""
    assert await firestore_client.healthcheck() is True
