"""User related endpoints.

This module provides REST API endpoints for user management operations,
including creating, reading, updating, and deleting users.
"""

__all__ = ["router"]

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

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
async def get_user(
    db: Annotated[DBClient, Depends(get_db)], user: Annotated[User, Depends(authorize_user(AppConfig))]
) -> UserGetResponseModel:
    """Retrieve the current user.

    Args:
        db: Database client dependency for database operations.
        user: User dependency for the authenticated user.

    Returns:
        A UserGetResponseModel object representing the current user.

    Raises:
        HTTPException: If the current user is not found.

    """
    user_dao = UserDAO(db)
    try:
        user = await user_dao.get_by_id(user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error retrieving user {user.id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

    return UserGetResponseModel.model_validate(user)


@router.put("", response_model=UserGetResponseModel, description="Update a user by ID")
async def update_user(
    user_model: UserUpdateRequestModel,
    db: Annotated[DBClient, Depends(get_db)],
    user: Annotated[User, Depends(authorize_user(AppConfig))],
) -> UserGetResponseModel:
    """Update an existing user's information.

    Args:
        user_model: UserUpdateRequestModel containing the updated user information.
        db: Database client dependency for database operations.
        user: User dependency for the authenticated user.

    Returns:
        A UserGetResponseModel object representing the updated user.

    Raises:
        HTTPException: If the current user is not found or validation fails.

    """
    user_dao = UserDAO(db)
    try:
        updated_user = await user_dao.update(user.id, user_model.name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error updating user {user.id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

    return UserGetResponseModel.model_validate(updated_user)
