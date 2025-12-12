"""Authentication client for encoding and decoding JWT tokens."""

from datetime import datetime, timedelta, timezone

from jwt import decode, encode

from keychain.config import AppConfig
from keychain.utils import Singleton


class AuthClient(metaclass=Singleton):
    """Client for performing JWT token operations.

    This class provides a wrapper around the JWT library for encoding
    and decoding tokens, using configuration from the application settings.
    It supports creating tokens with automatic expiration and validating
    existing tokens.
    """

    def __init__(self, config: AppConfig | None = None):
        """Initialize the authentication client.

        Creates an authentication client using JWT configuration from the
        application settings. If no config is provided, it will retrieve
        or create the default application configuration.

        Args:
            config: Optional application configuration. If None, the default
                configuration will be retrieved or created.

        """
        config = config or AppConfig.get_or_create()
        self.secret_key = config.auth.jwt_secret_key.get_secret_value()
        self.algorithm = config.auth.algorithm
        self.access_token_expire_minutes = config.auth.access_token_expire_minutes

    def encode_token(self, sub: str, exp: datetime | None = None) -> str:
        """Encode a JWT token with the given subject and optional expiration.

        Takes a subject (typically a user identifier) and optional expiration time,
        and encodes them into a JWT token string. If no expiration is provided,
        it will be set based on the configuration.

        Args:
            sub: The subject of the token (typically a user ID or username).
            exp: Optional expiration datetime. If None, expiration will be set
                based on access_token_expire_minutes from configuration.

        Returns:
            The encoded JWT token as a string.

        """
        # Build the payload
        payload = {"sub": sub}

        # Add expiration time
        if exp is None:
            exp = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
        payload["exp"] = exp

        # Encode the token
        return encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> dict:
        """Decode and validate a JWT token.

        Takes a JWT token string, validates it, and returns the decoded payload.

        Args:
            token: The JWT token string to decode.

        Returns:
            Dictionary containing the decoded token payload.

        Raises:
            jwt.ExpiredSignatureError: If the token has expired.
            jwt.InvalidTokenError: If the token is invalid or malformed.

        """
        return decode(
            token, self.secret_key, algorithms=[self.algorithm], options={"verify_signature": True, "verify_exp": True}
        )
