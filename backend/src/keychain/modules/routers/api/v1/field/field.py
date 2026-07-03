"""API v1 routes for managing fields."""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from loguru import logger
from sqlalchemy.exc import NoResultFound, SQLAlchemyError

from keychain.config import AppConfig
from keychain.modules.middlewares.dependencies import authorize_user, get_db
from keychain.modules.routers.models.base.metadata import PaginationMetadata
from keychain.modules.routers.models.request.field import (
    FieldCreateRequestModel,
    FieldUpdateRequestModel,
    GetAllFieldsQuery,
)
from keychain.modules.routers.models.response.field import FieldGetResponseModel, GetAllFieldsResponse, SimpleFieldGet
from keychain.services.daos.field import FieldDAO
from keychain.services.db_client.client import DBClient
from keychain.services.db_client.models.password import Password
from keychain.services.db_client.models.user import User

router = APIRouter(prefix="/field", tags=["Fields Management"])


@router.get("", response_model=GetAllFieldsResponse, description="Get all fields")
async def get_fields(
    db: Annotated[DBClient, Depends(get_db)],
    user: Annotated[User, Depends(authorize_user(AppConfig))],
    query: Annotated[GetAllFieldsQuery, Query(description="Query parameters for getting all fields")],
) -> GetAllFieldsResponse:
    """Retrieve all fields belonging to the authenticated user.

    Args:
        db (DBClient): The database client dependency.
        user (User): The authenticated user resolved from the request.
        query (GetAllFieldsQuery): Pagination and filtering query parameters.

    Returns:
        GetAllFieldsResponse: The matching fields along with pagination metadata.

    Raises:
        HTTPException: With status 500 if a database error occurs.

    """
    field_dao = FieldDAO(db)
    query_filters = field_dao.parse_filters(query.filters)
    filters = field_dao.concat_filters([*query_filters, Password.user_id == user.id])

    try:
        data, total = await field_dao.get_all(filters=filters, **query.model_dump(exclude="filters"))
        metadata = PaginationMetadata(total=total, **query.model_dump())
    except SQLAlchemyError as e:
        logger.exception("Error retrieving fields", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
        ) from e

    return GetAllFieldsResponse(data=[SimpleFieldGet.model_validate(field) for field in data], metadata=metadata)


@router.get("/{field_id}", response_model=FieldGetResponseModel, description="Get a field by ID")
async def get_field(
    field_id: Annotated[int, Path(description="The unique identifier of the field to retrieve")],
    db: Annotated[DBClient, Depends(get_db)],
    user: Annotated[User, Depends(authorize_user(AppConfig))],
) -> FieldGetResponseModel:
    """Retrieve a single field by its identifier for the authenticated user.

    Args:
        field_id (int): The unique identifier of the field to retrieve.
        db (DBClient): The database client dependency.
        user (User): The authenticated user resolved from the request.

    Returns:
        FieldGetResponseModel: The requested field.

    Raises:
        HTTPException: With status 404 if the field is not found, or status 500
            if a database error occurs.

    """
    field_dao = FieldDAO(db)
    try:
        field = await field_dao.get_by_pk(field_id, filters=[Password.user_id == user.id])
    except NoResultFound as e:
        logger.warning("Field not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found") from e
    except SQLAlchemyError as e:
        logger.exception("Error retrieving field", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
        ) from e

    return FieldGetResponseModel.model_validate(field)


@router.post(
    "",
    response_model=FieldGetResponseModel,
    status_code=status.HTTP_201_CREATED,
    description="Create a new field",
    dependencies=[Depends(authorize_user(AppConfig))],
)
async def create_field(
    body: Annotated[FieldCreateRequestModel, Body(description="The field to create")],
    db: Annotated[DBClient, Depends(get_db)],
    user: Annotated[User, Depends(authorize_user(AppConfig))],
) -> FieldGetResponseModel:
    """Create a new field for the authenticated user.

    Args:
        body (FieldCreateRequestModel): The field data to create.
        db (DBClient): The database client dependency.
        user (User): The authenticated user resolved from the request.

    Returns:
        FieldGetResponseModel: The newly created field.

    Raises:
        HTTPException: With status 404 if the parent password is not found, or
            status 500 if a database error occurs.

    """
    field_dao = FieldDAO(db)
    try:
        field = await field_dao.create(**body.model_dump(), filters=[Password.user_id == user.id])
    except NoResultFound as e:
        logger.warning("Password not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Password not found") from e
    except SQLAlchemyError as e:
        logger.exception("Error creating field", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
        ) from e

    return FieldGetResponseModel.model_validate(field)


@router.put("/{field_id}", response_model=FieldGetResponseModel, description="Update a field by ID")
async def update_field(
    field_id: Annotated[int, Path(description="The unique identifier of the field to update")],
    body: Annotated[FieldUpdateRequestModel, Body(description="The field to update")],
    db: Annotated[DBClient, Depends(get_db)],
    user: Annotated[User, Depends(authorize_user(AppConfig))],
) -> FieldGetResponseModel:
    """Update an existing field by its identifier for the authenticated user.

    Args:
        field_id (int): The unique identifier of the field to update.
        body (FieldUpdateRequestModel): The field data to apply.
        db (DBClient): The database client dependency.
        user (User): The authenticated user resolved from the request.

    Returns:
        FieldGetResponseModel: The updated field.

    Raises:
        HTTPException: With status 404 if the field is not found, or status 500
            if a database error occurs.

    """
    field_dao = FieldDAO(db)
    try:
        field = await field_dao.update(field_id, **body.model_dump(), filters=[Password.user_id == user.id])
    except NoResultFound as e:
        logger.warning("Field not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found") from e
    except SQLAlchemyError as e:
        logger.exception("Error updating field", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
        ) from e

    return FieldGetResponseModel.model_validate(field)


@router.delete("/{field_id}", status_code=status.HTTP_204_NO_CONTENT, description="Delete a field by ID")
async def delete_field(
    field_id: Annotated[int, Path(description="The unique identifier of the field to delete")],
    db: Annotated[DBClient, Depends(get_db)],
    user: Annotated[User, Depends(authorize_user(AppConfig))],
) -> None:
    """Delete a field by its identifier for the authenticated user.

    Args:
        field_id (int): The unique identifier of the field to delete.
        db (DBClient): The database client dependency.
        user (User): The authenticated user resolved from the request.

    Returns:
        None.

    Raises:
        HTTPException: With status 404 if the field is not found, or status 500
            if a database error occurs.

    """
    field_dao = FieldDAO(db)
    try:
        await field_dao.delete(field_id, filters=[Password.user_id == user.id])
    except NoResultFound as e:
        logger.warning("Field not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found") from e
    except SQLAlchemyError as e:
        logger.exception("Error deleting field", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
        ) from e
