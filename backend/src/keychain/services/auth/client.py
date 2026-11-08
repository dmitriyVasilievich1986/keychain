"""Authentication client for encoding and decoding JWT tokens."""

__all__ = ("AuthClient",)

from datetime import datetime, timedelta, timezone

from jwt import decode, encode

from keychain.config import AppConfig
from keychain.services.cryptography.client import CryptographyClient

from .models import DecodedToken, EncodedToken


class AuthClient:
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
        config = config or AppConfig()
        self.secret_key = config.auth.jwt_secret_key.get_secret_value()
        self.algorithm = config.auth.algorithm
        self.access_token_expire_minutes = config.auth.access_token_expire_minutes

    def encode_token(self, sub: str, dek: bytes, exp: datetime | None = None) -> EncodedToken:
        """Encode a JWT token with the given subject and optional expiration.

        Takes a subject (typically a user identifier), the user's data
        encryption key and optional expiration time, and encodes them into a
        JWT token string. The data encryption key is sealed with the
        application secret key before being embedded. If no expiration is
        provided, it will be set based on the configuration.

        Args:
            sub: The subject of the token (typically a user ID or username).
            dek: The user's plaintext data encryption key.
            exp: Optional expiration datetime. If None, expiration will be set
                based on access_token_expire_minutes from configuration.

        Returns:
            EncodedToken model containing the encoded token payload.

        """
        # Build the payload
        payload = {"sub": sub, "ek": CryptographyClient().seal_dek(dek)}

        # Add expiration time
        if exp is None:
            exp = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)

        # Encode the token
        return EncodedToken(
            access_token=encode(payload | {"exp": exp}, self.secret_key, algorithm=self.algorithm), expires_at=exp
        )

    def decode_token(self, token: str) -> DecodedToken:
        """Decode and validate a JWT token.

        Takes a JWT token string, validates it, and returns the decoded payload.

        Args:
            token: The JWT token string to decode.

        Returns:
            DecodedToken model containing the decoded token payload.

        Raises:
            jwt.ExpiredSignatureError: If the token has expired.
            jwt.InvalidTokenError: If the token is invalid or malformed.

        """
        return DecodedToken.model_validate(
            decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_signature": True, "verify_exp": True},
            )
        )
