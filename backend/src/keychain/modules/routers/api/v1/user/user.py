"""User router for retrieving and updating the current user."""

__all__ = ("router",)

from typing import Annotated

import structlog
from fastapi import APIRouter, Body, Depends, HTTPException, status
from google.api_core.exceptions import GoogleAPICallError, NotFound

from keychain.modules.middlewares.dependencies import authorize_user, get_users_db
from keychain.modules.routers.models.request.user import UserUpdateRequestModel
from keychain.modules.routers.models.response.user import UserGetResponseModel
from keychain.services.daos import UserDAO
from keychain.services.daos.firestore.models import User
from keychain.services.db_client.firestore import UsersFirestoreClient

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
    users_db: Annotated[UsersFirestoreClient, Depends(get_users_db)],
    user: Annotated[User, Depends(authorize_user)],
) -> UserGetResponseModel:
    """Update the authenticated user's details.

    Args:
        body (UserUpdateRequestModel): The request body with fields to update.
        users_db (UsersFirestoreClient): The users database client used to
            persist the update.
        user (User): The authenticated user resolved from the request token.

    Returns:
        UserGetResponseModel: The serialized updated user.

    Raises:
        HTTPException: 404 if the user no longer exists, or 500 on an
            unexpected Firestore error.

    """
    user_dao = UserDAO(users_db)

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
