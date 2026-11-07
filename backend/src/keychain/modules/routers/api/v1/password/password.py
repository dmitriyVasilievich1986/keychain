"""API v1 routes for managing user passwords."""

__all__ = ("router",)

from typing import Annotated

import structlog
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from sqlalchemy.exc import NoResultFound, SQLAlchemyError

from keychain.modules.middlewares.dependencies import authorize_user, get_db, get_user_dek
from keychain.modules.routers.models.base.metadata import PaginationMetadata
from keychain.modules.routers.models.request.password import (
    GetAllPasswordsQuery,
    PasswordCreateRequestModel,
    PasswordPatchRequestModel,
    PasswordUpdateRequestModel,
)
from keychain.modules.routers.models.response.password import (
    GetAllPasswordsResponse,
    PasswordGetResponseModel,
    SimplePasswordGet,
)
from keychain.services.daos.password import PasswordDAO
from keychain.services.db_client.client import DBClient
from keychain.services.db_client.models.password import Password
from keychain.services.db_client.models.user import User

logger = structlog.stdlib.get_logger(__name__)

router = APIRouter(prefix="/password", tags=["Passwords Management"])


@router.get("", response_model=GetAllPasswordsResponse, description="Get all passwords")
async def get_passwords(
    db: Annotated[DBClient, Depends(get_db)],
    user: Annotated[User, Depends(authorize_user)],
    query: Annotated[GetAllPasswordsQuery, Query(description="The query parameters for getting all passwords")],
) -> GetAllPasswordsResponse:
    """Retrieve all passwords belonging to the authenticated user.

    Args:
        db (DBClient): The database client dependency.
        user (User): The authenticated user resolved from the request.
        query (GetAllPasswordsQuery): Filtering and pagination parameters.

    Returns:
        GetAllPasswordsResponse: The paginated list of passwords with metadata.

    Raises:
        HTTPException: If an unexpected database error occurs (HTTP 500).

    """
    password_dao = PasswordDAO(db)
    filters = password_dao.concat_filters([Password.user_id == user.id], query.parsed_filters)

    try:
        data, total = await password_dao.get_all(filters=filters, **query.model_dump(exclude={"filters"}))
        metadata = PaginationMetadata(total=total, **query.model_dump())
    except SQLAlchemyError as e:
        logger.exception("Error retrieving passwords")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
        ) from e

    return GetAllPasswordsResponse(data=[SimplePasswordGet.model_validate(pwd) for pwd in data], metadata=metadata)


@router.get("/{password_id}", response_model=PasswordGetResponseModel, description="Get a password by ID")
async def get_password(
    password_id: Annotated[int, Path(description="The unique identifier of the password to retrieve")],
    db: Annotated[DBClient, Depends(get_db)],
    user: Annotated[User, Depends(authorize_user)],
    dek: Annotated[bytes, Depends(get_user_dek)],
) -> PasswordGetResponseModel:
    """Retrieve a single password by its ID for the authenticated user.

    Args:
        password_id (int): The unique identifier of the password to retrieve.
        db (DBClient): The database client dependency.
        user (User): The authenticated user resolved from the request.
        dek (bytes): The authenticated user's data encryption key.

    Returns:
        PasswordGetResponseModel: The requested password.

    Raises:
        HTTPException: If the password is not found (HTTP 404) or an
            unexpected database error occurs (HTTP 500).

    """
    password_dao = PasswordDAO(db)
    try:
        password = await password_dao.get_by_pk(password_id, filters=[Password.user_id == user.id])
    except NoResultFound as e:
        logger.warning("Password not found", password_id=password_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Password not found") from e
    except SQLAlchemyError as e:
        logger.exception("Error retrieving password")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
        ) from e

    return PasswordGetResponseModel.model_validate(password, context={"dek": dek})


@router.post(
    "",
    response_model=PasswordGetResponseModel,
    description="Create a new password",
    status_code=status.HTTP_201_CREATED,
)
async def create_password(
    body: Annotated[PasswordCreateRequestModel, Body(description="The request body for creating a new password")],
    db: Annotated[DBClient, Depends(get_db)],
    user: Annotated[User, Depends(authorize_user)],
    dek: Annotated[bytes, Depends(get_user_dek)],
) -> PasswordGetResponseModel:
    """Create a new password for the authenticated user.

    Args:
        body (PasswordCreateRequestModel): The data for the new password.
        db (DBClient): The database client dependency.
        user (User): The authenticated user resolved from the request.
        dek (bytes): The authenticated user's data encryption key.

    Returns:
        PasswordGetResponseModel: The newly created password.

    Raises:
        HTTPException: If an unexpected database error occurs (HTTP 500).

    """
    password_dao = PasswordDAO(db)

    try:
        password = await password_dao.create(**body.model_dump(), user_id=user.id)
    except SQLAlchemyError as e:
        logger.exception("Error creating password")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
        ) from e

    return PasswordGetResponseModel.model_validate(password, context={"dek": dek})


@router.put("/{password_id}", response_model=PasswordGetResponseModel, description="Update a password by ID")
async def update_password(
    password_id: Annotated[int, Path(description="The unique identifier of the password to update")],
    body: Annotated[PasswordUpdateRequestModel, Body(description="The request body for updating a password")],
    db: Annotated[DBClient, Depends(get_db)],
    user: Annotated[User, Depends(authorize_user)],
    dek: Annotated[bytes, Depends(get_user_dek)],
) -> PasswordGetResponseModel:
    """Fully update a password by its ID for the authenticated user.

    Args:
        password_id (int): The unique identifier of the password to update.
        body (PasswordUpdateRequestModel): The full set of updated values.
        db (DBClient): The database client dependency.
        user (User): The authenticated user resolved from the request.
        dek (bytes): The authenticated user's data encryption key.

    Returns:
        PasswordGetResponseModel: The updated password.

    Raises:
        HTTPException: If the password is not found (HTTP 404) or an
            unexpected database error occurs (HTTP 500).

    """
    password_dao = PasswordDAO(db)

    try:
        password = await password_dao.update(password_id, **body.model_dump(), filters=[Password.user_id == user.id])
    except NoResultFound as e:
        logger.warning("Password not found", password_id=password_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Password not found") from e
    except SQLAlchemyError as e:
        logger.exception("Error updating password")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
        ) from e

    return PasswordGetResponseModel.model_validate(password, context={"dek": dek})


@router.patch("/{password_id}", response_model=PasswordGetResponseModel, description="Patch a password by ID")
async def patch_password(
    password_id: Annotated[int, Path(description="The unique identifier of the password to update")],
    body: Annotated[PasswordPatchRequestModel, Body(description="The request body for updating a password")],
    db: Annotated[DBClient, Depends(get_db)],
    user: Annotated[User, Depends(authorize_user)],
    dek: Annotated[bytes, Depends(get_user_dek)],
) -> PasswordGetResponseModel:
    """Update a password partially by its ID for the authenticated user.

    Only the fields explicitly provided in the request body are updated.

    Args:
        password_id (int): The unique identifier of the password to update.
        body (PasswordPatchRequestModel): The subset of values to update.
        db (DBClient): The database client dependency.
        user (User): The authenticated user resolved from the request.
        dek (bytes): The authenticated user's data encryption key.

    Returns:
        PasswordGetResponseModel: The updated password.

    Raises:
        HTTPException: If the password is not found (HTTP 404) or an
            unexpected database error occurs (HTTP 500).

    """
    password_dao = PasswordDAO(db)

    try:
        password = await password_dao.update(
            password_id, **body.model_dump(exclude_unset=True), filters=[Password.user_id == user.id]
        )
    except NoResultFound as e:
        logger.warning("Password not found", password_id=password_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Password not found") from e
    except SQLAlchemyError as e:
        logger.exception("Error updating password")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
        ) from e

    return PasswordGetResponseModel.model_validate(password, context={"dek": dek})


@router.delete("/{password_id}", status_code=status.HTTP_204_NO_CONTENT, description="Delete a password by ID")
async def delete_password(
    password_id: Annotated[int, Path(description="The unique identifier of the password to delete")],
    db: Annotated[DBClient, Depends(get_db)],
    user: Annotated[User, Depends(authorize_user)],
) -> None:
    """Delete a password by its ID for the authenticated user.

    Args:
        password_id (int): The unique identifier of the password to delete.
        db (DBClient): The database client dependency.
        user (User): The authenticated user resolved from the request.

    Returns:
        None.

    Raises:
        HTTPException: If the password is not found (HTTP 404) or an
            unexpected database error occurs (HTTP 500).

    """
    password_dao = PasswordDAO(db)

    try:
        await password_dao.delete(password_id, filters=[Password.user_id == user.id])
    except NoResultFound as e:
        logger.warning("Password not found", password_id=password_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Password not found") from e
    except SQLAlchemyError as e:
        logger.exception("Error deleting password")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
        ) from e
