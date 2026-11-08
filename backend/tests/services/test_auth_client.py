"""Tests for :class:`AuthClient` token encoding."""

from keychain.config import AppConfig
from keychain.services.auth.client import AuthClient
from keychain.services.cryptography import CryptographyClient


def test_token_carries_sealed_dek(app_config: AppConfig) -> None:
    """The encoded token contains the sealed data key, which opens to the original."""
    crypto = CryptographyClient(app_config)
    dek = crypto.create_user_keys("secret").dek
    auth = AuthClient(app_config)

    decoded = auth.decode_token(auth.encode_token("1", dek).access_token)

    assert decoded.user_id == "1"
    assert dek.decode() not in decoded.sealed_dek
    assert crypto.open_dek(decoded.sealed_dek) == dek
