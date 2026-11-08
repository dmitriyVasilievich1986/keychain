"""Utility for decoding a JWT token."""

__all__ = ("decode_jwt_token",)

import structlog
from fastapi import HTTPException, status
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, PyJWTError

from keychain.services.auth.client import AuthClient
from keychain.services.auth.models import DecodedToken

logger = structlog.stdlib.get_logger(__name__)


def decode_jwt_token(token: str) -> DecodedToken:
    """Decode and validate a user's bearer token.

    Args:
        token (str): The raw bearer token.

    Returns:
        DecodedToken: The decoded token payload.

    Raises:
        HTTPException: 401 if the token is invalid or expired.

    """
    auth_service = AuthClient()

    try:
        return auth_service.decode_token(token=token)
    except ExpiredSignatureError as e:
        logger.warning("Expired token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Expired token") from e
    except (InvalidTokenError, ValueError) as e:
        logger.exception("Invalid token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from e
    except PyJWTError as e:
        logger.exception("An unexpected error occurred")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="An unexpected error occurred") from e
