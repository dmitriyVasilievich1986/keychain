"""User authorization dependency for FastAPI endpoints.

This module provides dependency injection functions for authorizing users
via JWT tokens in HTTP Bearer authentication headers. It validates tokens,
retrieves user information from the database, and handles authentication errors.
"""

__all__ = ["authorize_user"]

from typing import Annotated, Any, Callable, Coroutine

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger

from keychain.config import AppConfig
from keychain.services.auth.client import AuthClient
from keychain.services.daos.user import UserDAO
from keychain.services.db_client.client import DBClient
from keychain.services.db_client.models.user import User

from .get_db import get_db

user_token = HTTPBearer(scheme_name="User Token")


def authorize_user(
    config: type[AppConfig],
) -> Callable[[Annotated[HTTPAuthorizationCredentials, Depends(user_token)]], Coroutine[Any, Any, User]]:
    """Create a FastAPI dependency for user authorization.

    This factory function creates a dependency that validates JWT tokens from
    HTTP Bearer authentication headers and retrieves the corresponding user
    from the database.

    Args:
        config: The application configuration class containing authentication settings.

    Returns:
        A dependency function that can be used with FastAPI's Depends() to inject
        an authorized User object into endpoint handlers.

    Raises:
        HTTPException: With status 401 if token is invalid or user not found.
        HTTPException: With status 500 if an unexpected error occurs.

    """

    async def _authorize_user(
        token_header: Annotated[HTTPAuthorizationCredentials, Depends(user_token)],
        db_client: Annotated[DBClient, Depends(get_db)],
    ) -> User:
        """Authorize a user based on their JWT token.

        Args:
            token_header: The HTTP Bearer token credentials from the request header.
            db_client: The database client for querying user information.

        Returns:
            The authenticated User object from the database.

        Raises:
            HTTPException: With status 401 if token is invalid or user not found.
            HTTPException: With status 500 if an unexpected error occurs during authorization.

        """
        auth_service = AuthClient(config=config.get_or_create())

        try:
            result = auth_service.decode_token(token=token_header.credentials)
        except ValueError as e:
            raise HTTPException(status_code=401, detail=str(e)) from e

        try:
            return await UserDAO(db_client).get_by_id(pk=result.user_id)
        except ValueError as e:
            raise HTTPException(status_code=401, detail=str(e)) from e
        except Exception as e:
            logger.error(f"Error authorizing user: {e}")
            raise HTTPException(status_code=500, detail=str(e)) from e

    return _authorize_user
