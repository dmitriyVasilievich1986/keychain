"""Cryptography client for encrypting and decrypting data using Fernet symmetric encryption."""

from cryptography.fernet import Fernet

from keychain.config import AppConfig
from keychain.utils import Singleton


class CryptographyClient(metaclass=Singleton):
    """Client for performing encryption and decryption operations.

    This class provides a wrapper around the Fernet symmetric encryption
    implementation, using a secret key from the application configuration.
    It supports encrypting and decrypting string data securely.
    """

    def __init__(self, config: AppConfig | None = None):
        """Initialize the cryptography client with a secret key.

        Creates a Fernet cipher instance using the secret key from the
        application configuration. If no config is provided, it will
        retrieve or create the default application configuration.

        Args:
            config: Optional application configuration. If None, the default
                configuration will be retrieved or created.

        """
        config = config or AppConfig.get_or_create()
        self.fernet = Fernet(config.cryptography.secret_key.get_secret_value().encode())

    def encrypt(self, data: str) -> str:
        """Encrypt a string using Fernet symmetric encryption.

        Takes a plaintext string, encrypts it using the configured Fernet
        cipher, and returns the encrypted data as a string.

        Args:
            data: The plaintext string to encrypt.

        Returns:
            The encrypted string representation of the data.

        """
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, data: str) -> str:
        """Decrypt a string that was encrypted with Fernet.

        Takes an encrypted string, decrypts it using the configured Fernet
        cipher, and returns the original plaintext string.

        Args:
            data: The encrypted string to decrypt.

        Returns:
            The decrypted plaintext string.

        Raises:
            cryptography.fernet.InvalidToken: If the encrypted data is
                invalid or was encrypted with a different key.

        """
        return self.fernet.decrypt(data.encode()).decode()
