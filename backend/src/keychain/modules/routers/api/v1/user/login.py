"""User login router for issuing access tokens."""

__all__ = ("router",)

from typing import Annotated

import structlog
from cryptography.fernet import InvalidToken
from fastapi import APIRouter, Body, Depends, HTTPException, status
from google.api_core.exceptions import GoogleAPICallError, NotFound
from jwt.exceptions import PyJWTError

from keychain.config import AppConfig
from keychain.modules.middlewares.dependencies import get_config, get_users_db
from keychain.modules.routers.models.request.user import (
    LoginRequestModel,
)
from keychain.modules.routers.models.response.user import AccessTokenResponseModel
from keychain.services.auth.client import AuthClient
from keychain.services.daos.firestore import UserDAO
from keychain.services.db_client.firestore import UsersFirestoreClient

logger = structlog.stdlib.get_logger(__name__)

router = APIRouter(prefix="/user")


@router.post("/login", response_model=AccessTokenResponseModel, description="Login a user")
async def login_user(
    body: Annotated[LoginRequestModel, Body(description="Login request body")],
    users_db: Annotated[UsersFirestoreClient, Depends(get_users_db)],
    config: Annotated[AppConfig, Depends(get_config)],
) -> AccessTokenResponseModel:
    """Authenticate a user and issue an access token.

    Args:
        body (LoginRequestModel): The login request containing username and
            password.
        users_db (UsersFirestoreClient): The users database client used to
            look up the user.
        config (AppConfig): The application config used to build the auth
            client.

    Returns:
        AccessTokenResponseModel: The response containing the access token.

    Raises:
        HTTPException: 404 if the username does not exist, 401 if the password
            is incorrect, or 500 on a database, encryption or token encoding
            error.

    Users created before per-user encryption keys were introduced cannot log
    in until they are migrated with ``keychain db migrate-fields-encryption``.

    """
    user_dao = UserDAO(users_db)
    try:
        user = await user_dao.get_by_username(body.username)
    except NotFound as e:
        logger.warning("User not found", username=body.username)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Username or password is incorrect") from e
    except GoogleAPICallError as e:
        logger.exception("Error logging in user")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
        ) from e

    if not user.verify_password(body.password):
        logger.warning("Invalid password", username=body.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username or password is incorrect")

    if not user.has_encryption_keys:
        logger.warning("User has no encryption keys", user_id=user.id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")

    try:
        dek = user.unwrap_dek(body.password)
    except InvalidToken as e:
        logger.exception("Error unwrapping user encryption key", user_id=user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
        ) from e

    auth_service = AuthClient(config=config)
    try:
        access_token = auth_service.encode_token(str(user.id), dek)
    except (ValueError, PyJWTError) as e:
        logger.exception("Error encoding access token")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
        ) from e

    return AccessTokenResponseModel(access_token=access_token.access_token, expires_at=access_token.expires_at)
