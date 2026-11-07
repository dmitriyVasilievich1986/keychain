"""Tests for :class:`CryptographyClient` per-user key handling."""

import pytest
from cryptography.fernet import InvalidToken

from keychain.config import AppConfig
from keychain.services.cryptography import CryptographyClient


@pytest.fixture
def client(app_config: AppConfig) -> CryptographyClient:
    """Return the cryptography client bound to the test config."""
    return CryptographyClient(app_config)


def test_unwrap_returns_generated_dek(client: CryptographyClient) -> None:
    """The wrapped key is recovered with the correct password."""
    keys = client.create_user_keys("secret")

    assert client.unwrap_dek("secret", keys.salt, keys.wrapped_dek) == keys.dek


def test_unwrap_with_wrong_password_fails(client: CryptographyClient) -> None:
    """A wrong password cannot unwrap the key."""
    keys = client.create_user_keys("secret")

    with pytest.raises(InvalidToken):
        client.unwrap_dek("wrong", keys.salt, keys.wrapped_dek)


def test_users_with_same_password_get_different_keys(client: CryptographyClient) -> None:
    """Random salts and keys make identical passwords produce unrelated material."""
    first = client.create_user_keys("secret")
    second = client.create_user_keys("secret")

    assert first.salt != second.salt
    assert first.dek != second.dek
    with pytest.raises(InvalidToken):
        client.unwrap_dek("secret", second.salt, first.wrapped_dek)


def test_rewrap_keeps_dek_and_rotates_salt(client: CryptographyClient) -> None:
    """Re-wrapping under a new password keeps the data key and changes the salt."""
    keys = client.create_user_keys("old")

    rewrapped = client.rewrap_dek("old", "new", keys.salt, keys.wrapped_dek)

    assert rewrapped.dek == keys.dek
    assert rewrapped.salt != keys.salt
    assert client.unwrap_dek("new", rewrapped.salt, rewrapped.wrapped_dek) == keys.dek
    with pytest.raises(InvalidToken):
        client.unwrap_dek("old", rewrapped.salt, rewrapped.wrapped_dek)


def test_rewrap_with_wrong_old_password_fails(client: CryptographyClient) -> None:
    """Re-wrapping requires the correct old password."""
    keys = client.create_user_keys("old")

    with pytest.raises(InvalidToken):
        client.rewrap_dek("wrong", "new", keys.salt, keys.wrapped_dek)


def test_encrypt_decrypt_round_trip(client: CryptographyClient) -> None:
    """Data encrypted with a user's key only decrypts with that key."""
    dek = client.create_user_keys("secret").dek
    other_dek = client.create_user_keys("secret").dek

    encrypted = client.encrypt("my-value", dek)

    assert client.decrypt(encrypted, dek) == "my-value"
    with pytest.raises(InvalidToken):
        client.decrypt(encrypted, other_dek)


def test_seal_open_round_trip(client: CryptographyClient) -> None:
    """A sealed key opens back to the original key."""
    dek = client.create_user_keys("secret").dek

    sealed = client.seal_dek(dek)

    assert sealed.encode() != dek
    assert client.open_dek(sealed) == dek
