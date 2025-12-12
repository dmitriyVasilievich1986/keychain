"""Field related endpoints.

This module provides REST API endpoints for field management operations,
including creating, reading, updating, and deleting fields.
"""

__all__ = ["router"]

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from loguru import logger

from keychain.config import AppConfig
from keychain.modules.middlewares.dependencies import authorize_user, get_db
from keychain.modules.routers.models.request.field import FieldCreateRequestModel, FieldUpdateRequestModel
from keychain.modules.routers.models.response.field import FieldGetResponseModel, FieldGetResponseModelSimple
from keychain.services.daos.field import FieldDAO
from keychain.services.db_client.client import DBClient
from keychain.services.db_client.models.user import User

router = APIRouter(prefix="/field", tags=["Fields Management"])


@router.get("", response_model=list[FieldGetResponseModelSimple], description="Get all fields")
async def get_fields(
    db: Annotated[DBClient, Depends(get_db)], user: Annotated[User, Depends(authorize_user(AppConfig))]
) -> list[FieldGetResponseModelSimple]:
    """Retrieve all fields from the database.

    Args:
        db: Database client dependency for database operations.
        user: User dependency for the authenticated user.

    Returns:
        A list of FieldGetResponseModelSimple objects representing all fields.

    """
    field_dao = FieldDAO(db, user.id)
    fields = await field_dao.get_all()
    return [FieldGetResponseModelSimple.model_validate(field) for field in fields]


@router.get("/{field_id}", response_model=FieldGetResponseModel, description="Get a field by ID")
async def get_field(
    field_id: Annotated[int, Path(description="The unique identifier of the field to retrieve")],
    db: Annotated[DBClient, Depends(get_db)],
    user: Annotated[User, Depends(authorize_user(AppConfig))],
) -> FieldGetResponseModel:
    """Retrieve a specific field by its ID.

    Args:
        field_id: The unique identifier of the field to retrieve passed as a path parameter.
        db: Database client dependency for database operations.
        user: User dependency for the authenticated user.

    Returns:
        A FieldGetResponseModel object representing the requested field.

    Raises:
        HTTPException: If the field with the given ID is not found.

    """
    field_dao = FieldDAO(db, user.id)
    try:
        field = await field_dao.get_by_id(field_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error retrieving field {field_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

    return FieldGetResponseModel.model_validate(field)


@router.post(
    "", response_model=FieldGetResponseModel, status_code=status.HTTP_201_CREATED, description="Create a new field"
)
async def create_field(
    field: FieldCreateRequestModel,
    db: Annotated[DBClient, Depends(get_db)],
    user: Annotated[User, Depends(authorize_user(AppConfig))],
) -> FieldGetResponseModel:
    """Create a new field in the database.

    Args:
        field: FieldCreateRequestModel containing the field's name, value, and password_id.
        db: Database client dependency for database operations.
        user: User dependency for the authenticated user.

    Returns:
        A FieldGetResponseModel object representing the newly created field.

    Raises:
        HTTPException: If validation fails or an error occurs during creation.

    """
    field_dao = FieldDAO(db, user.id)
    try:
        field = await field_dao.create(field.name, field.value, field.password_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error creating field: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

    return FieldGetResponseModel.model_validate(field)


@router.put("/{field_id}", response_model=FieldGetResponseModel, description="Update a field by ID")
async def update_field(
    field_id: Annotated[int, Path(description="The unique identifier of the field to update")],
    field: FieldUpdateRequestModel,
    db: Annotated[DBClient, Depends(get_db)],
    user: Annotated[User, Depends(authorize_user(AppConfig))],
) -> FieldGetResponseModel:
    """Update an existing field's information.

    Args:
        field_id: The unique identifier of the field to update passed as a path parameter.
        field: FieldUpdateRequestModel containing the updated field information.
        db: Database client dependency for database operations.
        user: User dependency for the authenticated user.

    Returns:
        A FieldGetResponseModel object representing the updated field.

    Raises:
        HTTPException: If the field with the given ID is not found or validation fails.

    """
    field_dao = FieldDAO(db, user.id)
    try:
        field = await field_dao.update(field_id, field.value)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error updating field {field_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

    return FieldGetResponseModel.model_validate(field)


@router.delete("/{field_id}", status_code=status.HTTP_204_NO_CONTENT, description="Delete a field by ID")
async def delete_field(
    field_id: Annotated[int, Path(description="The unique identifier of the field to delete")],
    db: Annotated[DBClient, Depends(get_db)],
    user: Annotated[User, Depends(authorize_user(AppConfig))],
) -> None:
    """Delete a field from the database.

    Args:
        field_id: The unique identifier of the field to delete passed as a path parameter.
        db: Database client dependency for database operations.
        user: User dependency for the authenticated user.

    Returns:
        None

    Raises:
        HTTPException: If the field with the given ID is not found.

    """
    field_dao = FieldDAO(db, user.id)
    try:
        await field_dao.delete(field_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error deleting field {field_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
