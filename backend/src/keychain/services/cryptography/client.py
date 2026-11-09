"""Cryptography client for encrypting and decrypting data using per-user keys.

Every user owns a random data encryption key (DEK) that encrypts their field
values. The DEK is stored wrapped (encrypted) by a key encryption key (KEK)
derived from the user's password with Argon2id. The application secret key is
used as an Argon2 secret (pepper), so a database dump alone is not enough to
brute-force the passwords, and to seal the DEK before it is embedded into an
access token.
"""

__all__ = ("CryptographyClient",)

import base64
import os
from warnings import deprecated

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id

from keychain.config import AppConfig

from .models import UserKeys


class CryptographyClient:
    """Client for performing encryption and decryption operations.

    This class wraps Fernet symmetric encryption and Argon2id key derivation.
    The secret key from the application configuration acts as a pepper for the
    key derivation and as the key used to seal data encryption keys for
    transport inside access tokens.
    """

    _salt_length: int = 16
    _key_length: int = 32
    _argon2_iterations: int = 3
    _argon2_lanes: int = 4
    _argon2_memory_cost_kib: int = 64 * 1024

    def __init__(self, config: AppConfig | None = None):
        """Initialize the cryptography client with a secret key.

        Args:
            config: Optional application configuration. If None, the default
                configuration will be retrieved or created.

        """
        config = config or AppConfig()
        secret_key = config.cryptography.secret_key.get_secret_value().encode()
        self._pepper = secret_key
        self.fernet = Fernet(secret_key)

    def derive_kek(self, password: str, salt: bytes) -> Fernet:
        """Derive a key encryption key from a password and salt.

        Args:
            password: The user's plaintext password.
            salt: The user's random salt.

        Returns:
            A Fernet cipher built from the derived key.

        """
        kdf = Argon2id(
            salt=salt,
            length=self._key_length,
            iterations=self._argon2_iterations,
            lanes=self._argon2_lanes,
            memory_cost=self._argon2_memory_cost_kib,
            secret=self._pepper,
        )
        return Fernet(base64.urlsafe_b64encode(kdf.derive(password.encode())))

    def create_user_keys(self, password: str, dek: bytes | None = None) -> UserKeys:
        """Generate a salt and wrap a data encryption key with the password.

        Args:
            password: The user's plaintext password.
            dek: An existing data encryption key to wrap. If None, a new random
                key is generated.

        Returns:
            The generated key material.

        """
        salt = os.urandom(self._salt_length)
        dek = dek or Fernet.generate_key()
        wrapped_dek = self.derive_kek(password, salt).encrypt(dek).decode()
        return UserKeys(salt=salt, wrapped_dek=wrapped_dek, dek=dek)

    def unwrap_dek(self, password: str, salt: bytes, wrapped_dek: str) -> bytes:
        """Recover a user's data encryption key using their password.

        Args:
            password: The user's plaintext password.
            salt: The user's salt.
            wrapped_dek: The wrapped data encryption key stored for the user.

        Returns:
            The plaintext data encryption key.

        Raises:
            cryptography.fernet.InvalidToken: If the password is incorrect.

        """
        return self.derive_kek(password, salt).decrypt(wrapped_dek.encode())

    def rewrap_dek(self, old_password: str, new_password: str, salt: bytes, wrapped_dek: str) -> UserKeys:
        """Re-wrap a user's data encryption key under a new password.

        The data encryption key itself is unchanged, so data encrypted with it
        stays readable. A fresh salt is generated for the new password.

        Args:
            old_password: The user's current plaintext password.
            new_password: The user's new plaintext password.
            salt: The user's current salt.
            wrapped_dek: The currently stored wrapped data encryption key.

        Returns:
            The key material wrapped with the new password.

        Raises:
            cryptography.fernet.InvalidToken: If the old password is incorrect.

        """
        dek = self.unwrap_dek(old_password, salt, wrapped_dek)
        return self.create_user_keys(new_password, dek=dek)

    def encrypt(self, data: str, dek: bytes) -> str:
        """Encrypt a string with a user's data encryption key.

        Args:
            data: The plaintext string to encrypt.
            dek: The user's data encryption key.

        Returns:
            The encrypted string representation of the data.

        """
        return Fernet(dek).encrypt(data.encode()).decode()

    def decrypt(self, data: str, dek: bytes) -> str:
        """Decrypt a string with a user's data encryption key.

        Args:
            data: The encrypted string to decrypt.
            dek: The user's data encryption key.

        Returns:
            The decrypted plaintext string.

        Raises:
            cryptography.fernet.InvalidToken: If the data was encrypted with a
                different key or is invalid.

        """
        return Fernet(dek).decrypt(data.encode()).decode()

    def seal_dek(self, dek: bytes) -> str:
        """Encrypt a data encryption key with the application secret key.

        Used to embed the key into an access token without exposing it.

        Args:
            dek: The plaintext data encryption key.

        Returns:
            The sealed data encryption key.

        """
        return self.fernet.encrypt(dek).decode()

    def open_dek(self, sealed_dek: str) -> bytes:
        """Decrypt a data encryption key sealed with :meth:`seal_dek`.

        Args:
            sealed_dek: The sealed data encryption key.

        Returns:
            The plaintext data encryption key.

        Raises:
            cryptography.fernet.InvalidToken: If the sealed key is invalid.

        """
        return self.fernet.decrypt(sealed_dek.encode())

    @deprecated("Use decrypt instead")
    def legacy_decrypt(self, data: str) -> str:
        """Decrypt a string encrypted with the application-wide secret key.

        Only used to migrate data stored before per-user keys were introduced.

        Args:
            data: The encrypted string to decrypt.

        Returns:
            The decrypted plaintext string.

        Raises:
            cryptography.fernet.InvalidToken: If the data is invalid or was
                encrypted with a different key.

        """
        return self.fernet.decrypt(data.encode()).decode()
