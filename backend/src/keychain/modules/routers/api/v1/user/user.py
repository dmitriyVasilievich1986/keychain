"""User related endpoints.

This module provides REST API endpoints for user management operations,
including creating, reading, updating, and deleting users.
"""

__all__ = ["router"]

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from keychain.modules.middlewares.dependencies import get_db
from keychain.modules.routers.models.request.user import UserCreateRequestModel, UserUpdateRequestModel
from keychain.modules.routers.models.response.user import UserGetResponseModel, UserGetResponseModelSimple
from keychain.services.daos.user import UserDAO
from keychain.services.db_client.client import DBClient

router = APIRouter(prefix="/user", tags=["user"])


@router.get("", response_model=list[UserGetResponseModelSimple], description="Get all users")
async def get_users(db: Annotated[DBClient, Depends(get_db)]) -> list[UserGetResponseModelSimple]:
    """Retrieve all users from the database.

    Args:
        db: Database client dependency for database operations.

    Returns:
        A list of UserGetResponseModel objects representing all users.

    """
    user_dao = UserDAO(db)
    users = await user_dao.get_all()
    return [UserGetResponseModelSimple.model_validate(user) for user in users]


@router.get("/{user_id}", response_model=UserGetResponseModel, description="Get a user by ID")
async def get_user(user_id: int, db: Annotated[DBClient, Depends(get_db)]) -> UserGetResponseModel:
    """Retrieve a specific user by their ID.

    Args:
        user_id: The unique identifier of the user to retrieve.
        db: Database client dependency for database operations.

    Returns:
        A UserGetResponseModel object representing the requested user.

    Raises:
        HTTPException: If the user with the given ID is not found.

    """
    user_dao = UserDAO(db)
    try:
        user = await user_dao.get_by_id(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error retrieving user {user_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

    return UserGetResponseModel.model_validate(user)


@router.post("", response_model=UserGetResponseModel, description="Create a new user")
async def create_user(user: UserCreateRequestModel, db: Annotated[DBClient, Depends(get_db)]) -> UserGetResponseModel:
    """Create a new user in the database.

    Args:
        user: UserCreateRequestModel containing the user's name and password.
        db: Database client dependency for database operations.

    Returns:
        A UserGetResponseModel object representing the newly created user.

    Raises:
        HTTPException: If a user with the same name already exists or validation fails.

    """
    user_dao = UserDAO(db)
    try:
        user = await user_dao.create(user.name, user.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

    return UserGetResponseModel.model_validate(user)


@router.put("/{user_id}", response_model=UserGetResponseModel, description="Update a user by ID")
async def update_user(
    user_id: int, user: UserUpdateRequestModel, db: Annotated[DBClient, Depends(get_db)]
) -> UserGetResponseModel:
    """Update an existing user's information.

    Args:
        user_id: The unique identifier of the user to update.
        user: UserUpdateRequestModel containing the updated user information.
        db: Database client dependency for database operations.

    Returns:
        A UserGetResponseModel object representing the updated user.

    Raises:
        HTTPException: If the user with the given ID is not found or validation fails.

    """
    user_dao = UserDAO(db)
    try:
        user = await user_dao.update(user_id, user.name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

    return UserGetResponseModel.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, description="Delete a user by ID")
async def delete_user(user_id: int, db: Annotated[DBClient, Depends(get_db)]) -> None:
    """Delete a user from the database.

    Args:
        user_id: The unique identifier of the user to delete.
        db: Database client dependency for database operations.

    Returns:
        None

    Raises:
        HTTPException: If the user with the given ID is not found.

    """
    user_dao = UserDAO(db)
    try:
        await user_dao.delete(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
