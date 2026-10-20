"""User router for retrieving and updating the current user."""

__all__ = ("router",)

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from google.api_core.exceptions import GoogleAPICallError, NotFound
from loguru import logger

from keychain.config import AppConfig
from keychain.modules.middlewares.dependencies import authorize_user, get_config, get_firestore
from keychain.modules.routers.models.request.user import (
    UserUpdateRequestModel,
)
from keychain.modules.routers.models.response.user import UserGetResponseModel
from keychain.services.daos.firestore import UserDAO
from keychain.services.daos.firestore.models import User
from keychain.services.db_client.firestore import FirestoreClient

router = APIRouter(prefix="/user")


@router.get("/me", response_model=UserGetResponseModel, description="Get the current user")
async def get_user(user: Annotated[User, Depends(authorize_user(AppConfig))]) -> UserGetResponseModel:
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
    user: Annotated[User, Depends(authorize_user(AppConfig))],
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
        updated_user = await user_dao.update(str(user.id), **body.model_dump(), updated_at=datetime.now(timezone.utc))
    except NotFound as e:
        logger.warning(f"User not found: {user.id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found") from e
    except GoogleAPICallError as e:
        logger.exception(f"Error updating user {user.id}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
        ) from e

    return UserGetResponseModel.model_validate(updated_user)
