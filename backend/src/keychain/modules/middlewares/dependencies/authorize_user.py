"""FastAPI dependency for authorizing a user from a bearer token."""

__all__ = ["authorize_user"]

from typing import Annotated, Any, Callable, Coroutine

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, PyJWTError
from loguru import logger
from sqlalchemy.exc import NoResultFound, SQLAlchemyError

from keychain.config import AppConfig
from keychain.services.auth.client import AuthClient
from keychain.services.daos.user import UserDAO
from keychain.services.db_client.client import DBClient
from keychain.services.db_client.models.user import User

from .get_db import get_db

user_token = HTTPBearer(scheme_name="User Token")


def authorize_user(
    config: type[AppConfig],
) -> Callable[[HTTPAuthorizationCredentials, DBClient], Coroutine[Any, Any, User]]:
    """Build a FastAPI dependency that authorizes a user from a bearer token.

    Args:
        config (type[AppConfig]): The application config class used to build
            the authentication client.

    Returns:
        Callable: An async dependency that resolves the authenticated user.

    """

    async def _authorize_user(
        token_header: Annotated[HTTPAuthorizationCredentials, Depends(user_token)],
        db_client: Annotated[DBClient, Depends(get_db)],
    ) -> User:
        """Resolve the authenticated user from the request's bearer token.

        Args:
            token_header (HTTPAuthorizationCredentials): The bearer credentials
                extracted from the request.
            db_client (DBClient): The database client used to look up the user.

        Returns:
            User: The authenticated user matching the token.

        Raises:
            HTTPException: 401 if the token is invalid or expired, 401 if the
                user does not exist, or 500 on an unexpected database error.

        """
        auth_service = AuthClient(config=config.get_or_create())

        try:
            result = auth_service.decode_token(token=token_header.credentials)
        except ExpiredSignatureError as e:
            logger.warning("Expired token")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Expired token") from e
        except (InvalidTokenError, ValueError) as e:
            logger.exception("Invalid token", exc_info=e)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from e
        except PyJWTError as e:
            logger.exception("An unexpected error occurred", exc_info=e)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="An unexpected error occurred") from e

        try:
            return await UserDAO(db_client).get_by_pk(pk=int(result.user_id))
        except NoResultFound as e:
            logger.warning(f"User not found: {result.user_id}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found") from e
        except SQLAlchemyError as e:
            logger.exception("Error retrieving user", exc_info=e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
            ) from e

    return _authorize_user
