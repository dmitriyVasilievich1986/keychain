"""Password related endpoints.

This module provides REST API endpoints for password management operations,
including creating, reading, updating, and deleting passwords.
"""

__all__ = ["router"]

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from loguru import logger

from keychain.config import AppConfig
from keychain.modules.middlewares.dependencies import authorize_user, get_db
from keychain.modules.routers.models.request.password import PasswordCreateRequestModel, PasswordUpdateRequestModel
from keychain.modules.routers.models.response.password import PasswordGetResponseModel, PasswordGetResponseModelSimple
from keychain.services.daos.password import PasswordDAO
from keychain.services.db_client.client import DBClient
from keychain.services.db_client.models.user import User

router = APIRouter(prefix="/password", tags=["Passwords Management"])


@router.get("", response_model=list[PasswordGetResponseModelSimple], description="Get all passwords")
async def get_passwords(
    db: Annotated[DBClient, Depends(get_db)], user: Annotated[User, Depends(authorize_user(AppConfig))]
) -> list[PasswordGetResponseModelSimple]:
    """Retrieve all passwords from the database.

    Args:
        db: Database client dependency for database operations.
        user: User dependency for the authenticated user.

    Returns:
        A list of PasswordGetResponseModelSimple objects representing all passwords.

    """
    password_dao = PasswordDAO(db, user.id)
    passwords = await password_dao.get_all()
    return [PasswordGetResponseModelSimple.model_validate({"id": pwd.id, "name": pwd.name}) for pwd in passwords]


@router.get("/{password_id}", response_model=PasswordGetResponseModel, description="Get a password by ID")
async def get_password(
    password_id: Annotated[int, Path(description="The unique identifier of the password to retrieve")],
    db: Annotated[DBClient, Depends(get_db)],
    user: Annotated[User, Depends(authorize_user(AppConfig))],
) -> PasswordGetResponseModel:
    """Retrieve a specific password by its ID.

    Args:
        password_id: The unique identifier of the password to retrieve passed as a path parameter.
        db: Database client dependency for database operations.
        user: User dependency for the authenticated user.

    Returns:
        A PasswordGetResponseModel object representing the requested password.

    Raises:
        HTTPException: If the password with the given ID is not found.

    """
    password_dao = PasswordDAO(db, user.id)
    try:
        password = await password_dao.get_by_id(password_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error retrieving password {password_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

    return PasswordGetResponseModel.model_validate(password)


@router.post("", response_model=PasswordGetResponseModel, description="Create a new password")
async def create_password(
    password: PasswordCreateRequestModel,
    db: Annotated[DBClient, Depends(get_db)],
    user: Annotated[User, Depends(authorize_user(AppConfig))],
) -> PasswordGetResponseModel:
    """Create a new password in the database.

    Args:
        password: PasswordCreateRequestModel containing the password's name, user_id, and optional image_url.
        db: Database client dependency for database operations.
        user: User dependency for the authenticated user.

    Returns:
        A PasswordGetResponseModel object representing the newly created password.

    Raises:
        HTTPException: If validation fails or an error occurs during creation.

    """
    password_dao = PasswordDAO(db, user.id)
    try:
        password = await password_dao.create(password.name, user.id, password.image_url)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error creating password: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

    return PasswordGetResponseModel.model_validate(password)


@router.put("/{password_id}", response_model=PasswordGetResponseModel, description="Update a password by ID")
async def update_password(
    password_id: Annotated[int, Path(description="The unique identifier of the password to update")],
    password: PasswordUpdateRequestModel,
    db: Annotated[DBClient, Depends(get_db)],
    user: Annotated[User, Depends(authorize_user(AppConfig))],
) -> PasswordGetResponseModel:
    """Update an existing password's information.

    Args:
        password_id: The unique identifier of the password to update passed as a path parameter.
        password: PasswordUpdateRequestModel containing the updated password information.
        db: Database client dependency for database operations.
        user: User dependency for the authenticated user.

    Returns:
        A PasswordGetResponseModel object representing the updated password.

    Raises:
        HTTPException: If the password with the given ID is not found or validation fails.

    """
    password_dao = PasswordDAO(db, user.id)
    try:
        password = await password_dao.update(password_id, password.name, password.image_url)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error updating password {password_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

    return PasswordGetResponseModel.model_validate(password)


@router.delete("/{password_id}", status_code=status.HTTP_204_NO_CONTENT, description="Delete a password by ID")
async def delete_password(
    password_id: Annotated[int, Path(description="The unique identifier of the password to delete")],
    db: Annotated[DBClient, Depends(get_db)],
    user: Annotated[User, Depends(authorize_user(AppConfig))],
) -> None:
    """Delete a password from the database.

    Args:
        password_id: The unique identifier of the password to delete passed as a path parameter.
        db: Database client dependency for database operations.
        user: User dependency for the authenticated user.

    Returns:
        None

    Raises:
        HTTPException: If the password with the given ID is not found.

    """
    password_dao = PasswordDAO(db, user.id)
    try:
        await password_dao.delete(password_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error deleting password {password_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
