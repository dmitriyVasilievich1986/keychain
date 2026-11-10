"""FastAPI dependencies for authorizing a user from a bearer token."""

__all__ = ("authorize_user", "get_user_dek")

from typing import Annotated
from uuid import UUID

import structlog
from cryptography.fernet import InvalidToken
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.api_core.exceptions import GoogleAPICallError, NotFound

from keychain.config import AppConfig
from keychain.services.cryptography.client import CryptographyClient
from keychain.services.daos.firestore import UserDAO
from keychain.services.daos.firestore.models import User
from keychain.services.db_client.firestore import FirestoreClient
from keychain.utils.decode_token import decode_jwt_token

from .get_config import get_config
from .get_firestore import get_firestore

logger = structlog.stdlib.get_logger(__name__)

user_token = HTTPBearer(scheme_name="User Token")


async def authorize_user(
    token_header: Annotated[HTTPAuthorizationCredentials, Depends(user_token)],
    firestore: Annotated[FirestoreClient, Depends(get_firestore)],
    config: Annotated[AppConfig, Depends(get_config)],
) -> User:
    """Resolve the authenticated user from the request's bearer token.

    The authenticated user's id is bound to structlog's context vars as
    ``user_id`` for the rest of the request.

    Args:
        token_header (HTTPAuthorizationCredentials): The bearer credentials
            extracted from the request.
        firestore (FirestoreClient): The Firestore client used to look up
            the user.
        config (AppConfig): The application config providing the users
            collection name.

    Returns:
        User: The authenticated user matching the token.

    Raises:
        HTTPException: 401 if the token is invalid or expired, 401 if the
            user does not exist, or 500 on an unexpected Firestore error.

    """
    result = decode_jwt_token(token_header.credentials)

    try:
        user_id = UUID(result.user_id)
    except ValueError as e:
        logger.warning("Invalid user ID in token", user_id=result.user_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from e

    try:
        user = await UserDAO(firestore, collection_name=config.db.users.collection_name).get_by_id(str(user_id))
    except NotFound as e:
        logger.warning("User not found", user_id=result.user_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found") from e
    except GoogleAPICallError as e:
        logger.exception("Error retrieving user")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
        ) from e

    structlog.contextvars.bind_contextvars(user_id=user.id)
    return user


def get_user_dek(token_header: Annotated[HTTPAuthorizationCredentials, Depends(user_token)]) -> bytes:
    """Resolve the user's data encryption key from the request's bearer token.

    Args:
        token_header (HTTPAuthorizationCredentials): The bearer credentials
            extracted from the request.

    Returns:
        bytes: The user's plaintext data encryption key.

    Raises:
        HTTPException: 401 if the token or the sealed key is invalid.

    """
    result = decode_jwt_token(token_header.credentials)

    try:
        return CryptographyClient().open_dek(result.sealed_dek)
    except InvalidToken as e:
        logger.warning("Invalid encryption key in token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from e
