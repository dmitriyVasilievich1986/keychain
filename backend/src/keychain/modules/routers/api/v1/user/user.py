"""User router for retrieving and updating the current user."""

__all__ = ("router",)

from typing import Annotated

import structlog
from cryptography.fernet import InvalidToken
from fastapi import APIRouter, Body, Depends, HTTPException, status
from google.api_core.exceptions import GoogleAPICallError, NotFound
from jwt.exceptions import PyJWTError

from keychain.config import AppConfig
from keychain.modules.middlewares.dependencies import authorize_user, get_config, get_firestore
from keychain.modules.routers.models.request.user import (
    UserPasswordChangeRequestModel,
    UserUpdateRequestModel,
)
from keychain.modules.routers.models.response.user import AccessTokenResponseModel, UserGetResponseModel
from keychain.services.auth.client import AuthClient
from keychain.services.daos import EncryptionKeysMissingError, InvalidPasswordError, UserDAO
from keychain.services.daos.firestore.models import User
from keychain.services.db_client.firestore import FirestoreClient

logger = structlog.stdlib.get_logger(__name__)

router = APIRouter(prefix="/user")


@router.get("/me", response_model=UserGetResponseModel, description="Get the current user")
async def get_user(user: Annotated[User, Depends(authorize_user)]) -> UserGetResponseModel:
    """Return the currently authenticated user.

    Args:
        user (User): The authenticated user resolved from the request token.

    Returns:
        UserGetResponseModel: The serialized current user.

    """
    return UserGetResponseModel.model_validate(user)


@router.put("", response_model=UserGetResponseModel, description="Update a user by ID")
async def update_user(
    body: Annotated[UserUpdateRequestModel, Body(description="Update user request body")],
    firestore: Annotated[FirestoreClient, Depends(get_firestore)],
    config: Annotated[AppConfig, Depends(get_config)],
    user: Annotated[User, Depends(authorize_user)],
) -> UserGetResponseModel:
    """Update the authenticated user's details.

    Args:
        body (UserUpdateRequestModel): The request body with fields to update.
        firestore (FirestoreClient): The Firestore client used to persist
            the update.
        config (AppConfig): The application config providing the users
            collection name.
        user (User): The authenticated user resolved from the request token.

    Returns:
        UserGetResponseModel: The serialized updated user.

    Raises:
        HTTPException: 404 if the user no longer exists, or 500 on an
            unexpected Firestore error.

    """
    user_dao = UserDAO(firestore, collection_name=config.db.users.collection_name)

    try:
        updated_user = await user_dao.update(user.id, **body.model_dump())
    except NotFound as e:
        logger.warning("User not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found") from e
    except GoogleAPICallError as e:
        logger.exception("Error updating user")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
        ) from e

    return UserGetResponseModel.model_validate(updated_user)


@router.put("/password", response_model=AccessTokenResponseModel, description="Change the current user's password")
async def change_password(
    body: Annotated[UserPasswordChangeRequestModel, Body(description="Change password request body")],
    firestore: Annotated[FirestoreClient, Depends(get_firestore)],
    config: Annotated[AppConfig, Depends(get_config)],
    user: Annotated[User, Depends(authorize_user)],
) -> AccessTokenResponseModel:
    """Change the authenticated user's password.

    The user's data encryption key is re-wrapped with the new password, so all
    stored fields stay readable. A new access token is issued.

    Args:
        body (UserPasswordChangeRequestModel): The current and new passwords.
        firestore (FirestoreClient): The Firestore client used to persist the
            change.
        config (AppConfig): The application config providing the users
            collection name and used to build the auth client.
        user (User): The authenticated user resolved from the request token.

    Returns:
        AccessTokenResponseModel: A new access token for the user.

    Raises:
        HTTPException: 400 if the current password is incorrect, 404 if the
            user no longer exists, or 500 on a Firestore, encryption or token
            encoding error.

    """
    user_dao = UserDAO(firestore, collection_name=config.db.users.collection_name)

    try:
        updated_user = await user_dao.reset_password(user.id, body.old_password, body.new_password)
        dek = updated_user.unwrap_dek(body.new_password)
    except InvalidPasswordError as e:
        logger.warning("Invalid current password")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect") from e
    except NotFound as e:
        logger.warning("User not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found") from e
    except (GoogleAPICallError, InvalidToken, EncryptionKeysMissingError) as e:
        logger.exception("Error changing user password")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
        ) from e

    try:
        access_token = AuthClient(config=config).encode_token(str(updated_user.id), dek)
    except (ValueError, PyJWTError) as e:
        logger.exception("Error encoding access token")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
        ) from e

    return AccessTokenResponseModel(access_token=access_token.access_token, expires_at=access_token.expires_at)
