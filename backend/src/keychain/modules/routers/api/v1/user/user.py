"""User router for retrieving and updating the current user."""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.exc import NoResultFound, SQLAlchemyError

from keychain.config import AppConfig
from keychain.modules.middlewares.dependencies import authorize_user, get_db
from keychain.modules.routers.models.request.user import (
    UserUpdateRequestModel,
)
from keychain.modules.routers.models.response.user import UserGetResponseModel
from keychain.services.daos.user import UserDAO
from keychain.services.db_client.client import DBClient
from keychain.services.db_client.models.user import User

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
    db: Annotated[DBClient, Depends(get_db)],
    user: Annotated[User, Depends(authorize_user(AppConfig))],
) -> UserGetResponseModel:
    """Update the authenticated user's details.

    Args:
        body (UserUpdateRequestModel): The request body with fields to update.
        db (DBClient): The database client used to persist the update.
        user (User): The authenticated user resolved from the request token.

    Returns:
        UserGetResponseModel: The serialized updated user.

    Raises:
        HTTPException: 404 if the user no longer exists, or 500 on an
            unexpected database error.

    """
    user_dao = UserDAO(db)

    try:
        updated_user = await user_dao.update(user.id, **body.model_dump())
    except NoResultFound as e:
        logger.warning(f"User not found: {user.id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found") from e
    except SQLAlchemyError as e:
        logger.exception(f"Error updating user {user.id}", exc_info="An unexpected error occurred")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
        ) from e

    return UserGetResponseModel.model_validate(updated_user)
