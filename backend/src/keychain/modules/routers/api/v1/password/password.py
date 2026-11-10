"""API v1 routes for managing user passwords."""

__all__ = ("router",)

from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from google.api_core.exceptions import GoogleAPICallError, NotFound

from keychain.modules.middlewares.dependencies import authorize_user, get_password_db, get_user_dek
from keychain.modules.routers.models.base.metadata import PaginationMetadata
from keychain.modules.routers.models.request.password import (
    GetAllPasswordsQuery,
    PasswordCreateRequestModel,
    PasswordFieldCreate,
    PasswordPatchRequestModel,
    PasswordUpdateRequestModel,
)
from keychain.modules.routers.models.response.password import (
    GetAllPasswordsResponse,
    PasswordGetResponseModel,
    SimplePasswordGet,
)
from keychain.services.daos.firestore import PasswordDAO
from keychain.services.daos.firestore.models import Field, FieldValue, Password, User
from keychain.services.db_client.firestore import PasswordsFirestoreClient
from keychain.utils.filter import Filter

logger = structlog.stdlib.get_logger(__name__)

router = APIRouter(prefix="/password", tags=["Passwords Management"])


async def get_owned_password(password_dao: PasswordDAO, password_id: UUID, user: User) -> Password:
    """Load a password and ensure it belongs to the given user.

    Args:
        password_dao (PasswordDAO): DAO used to load the password.
        password_id (UUID): The unique identifier of the password.
        user (User): The user who must own the password.

    Returns:
        Password: The requested password.

    Raises:
        NotFound: If the password does not exist or belongs to another user.

    """
    password = await password_dao.get_by_id(str(password_id))
    if password.user_id != str(user.id):
        raise NotFound(f"Password {password_id} not found")
    return password


def build_fields(fields: list[PasswordFieldCreate]) -> list[Field]:
    """Convert request fields into Firestore field models.

    Args:
        fields (list[PasswordFieldCreate]): The requested fields; their order
            in the list defines their position.

    Returns:
        list[Field]: The Firestore field models.

    """
    return [
        Field(
            name=field.name,
            position=position,
            values=[FieldValue(value=field_value.value) for field_value in field.values],
        )
        for position, field in enumerate(fields)
    ]


@router.get("", response_model=GetAllPasswordsResponse, description="Get all passwords")
async def get_passwords(
    password_db: Annotated[PasswordsFirestoreClient, Depends(get_password_db)],
    user: Annotated[User, Depends(authorize_user)],
    query: Annotated[GetAllPasswordsQuery, Query(description="The query parameters for getting all passwords")],
) -> GetAllPasswordsResponse:
    """Retrieve all passwords belonging to the authenticated user.

    Passwords marked as deleted are excluded unless ``query.show_deleted`` is set.

    Args:
        password_db (PasswordsFirestoreClient): The passwords database client.
        user (User): The authenticated user resolved from the request.
        query (GetAllPasswordsQuery): Filtering and pagination parameters.

    Returns:
        GetAllPasswordsResponse: The paginated list of passwords with metadata.

    Raises:
        HTTPException: If an unexpected Firestore error occurs (HTTP 500).

    """
    password_dao = PasswordDAO(password_db)
    filters = [Filter[str](column="user_id", operator="eq", value=str(user.id)), *(query.filters or [])]
    if not query.show_deleted:
        filters.append(Filter[str](column="deleted_at", operator="isnull", value=None))

    try:
        data, total = await password_dao.get_all(
            filters=filters, **query.model_dump(exclude={"filters", "show_deleted"})
        )
        metadata = PaginationMetadata(total=total, **query.model_dump(exclude={"show_deleted"}))
    except GoogleAPICallError as e:
        logger.exception("Error retrieving passwords")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
        ) from e

    return GetAllPasswordsResponse(data=[SimplePasswordGet.model_validate(pwd) for pwd in data], metadata=metadata)


@router.get("/{password_id}", response_model=PasswordGetResponseModel, description="Get a password by ID")
async def get_password(
    password_id: Annotated[UUID, Path(description="The unique identifier of the password to retrieve")],
    password_db: Annotated[PasswordsFirestoreClient, Depends(get_password_db)],
    user: Annotated[User, Depends(authorize_user)],
    dek: Annotated[bytes, Depends(get_user_dek)],
) -> PasswordGetResponseModel:
    """Retrieve a single password by its ID for the authenticated user.

    Args:
        password_id (UUID): The unique identifier of the password to retrieve.
        password_db (PasswordsFirestoreClient): The passwords database client.
        user (User): The authenticated user resolved from the request.
        dek (bytes): The authenticated user's data encryption key.

    Returns:
        PasswordGetResponseModel: The requested password.

    Raises:
        HTTPException: If the password is not found (HTTP 404) or an
            unexpected Firestore error occurs (HTTP 500).

    """
    password_dao = PasswordDAO(password_db, dek=dek)
    try:
        password = await get_owned_password(password_dao, password_id, user)
    except NotFound as e:
        logger.warning("Password not found", password_id=str(password_id))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Password not found") from e
    except GoogleAPICallError as e:
        logger.exception("Error retrieving password")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
        ) from e

    return PasswordGetResponseModel.model_validate(password)


@router.post(
    "",
    response_model=PasswordGetResponseModel,
    description="Create a new password",
    status_code=status.HTTP_201_CREATED,
)
async def create_password(
    body: Annotated[PasswordCreateRequestModel, Body(description="The request body for creating a new password")],
    password_db: Annotated[PasswordsFirestoreClient, Depends(get_password_db)],
    user: Annotated[User, Depends(authorize_user)],
    dek: Annotated[bytes, Depends(get_user_dek)],
) -> PasswordGetResponseModel:
    """Create a new password for the authenticated user.

    Args:
        body (PasswordCreateRequestModel): The data for the new password.
        password_db (PasswordsFirestoreClient): The passwords database client.
        user (User): The authenticated user resolved from the request.
        dek (bytes): The authenticated user's data encryption key.

    Returns:
        PasswordGetResponseModel: The newly created password.

    Raises:
        HTTPException: If an unexpected Firestore error occurs (HTTP 500).

    """
    password_dao = PasswordDAO(password_db, dek=dek)

    try:
        password = await password_dao.create(
            **body.model_dump(exclude={"fields"}),
            user_id=str(user.id),
            fields=build_fields(body.fields),
        )
    except GoogleAPICallError as e:
        logger.exception("Error creating password")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
        ) from e

    return PasswordGetResponseModel.model_validate(password)


@router.put("/{password_id}", response_model=PasswordGetResponseModel, description="Update a password by ID")
async def update_password(
    password_id: Annotated[UUID, Path(description="The unique identifier of the password to update")],
    body: Annotated[PasswordUpdateRequestModel, Body(description="The request body for updating a password")],
    password_db: Annotated[PasswordsFirestoreClient, Depends(get_password_db)],
    user: Annotated[User, Depends(authorize_user)],
    dek: Annotated[bytes, Depends(get_user_dek)],
) -> PasswordGetResponseModel:
    """Fully update a password by its ID for the authenticated user.

    Args:
        password_id (UUID): The unique identifier of the password to update.
        body (PasswordUpdateRequestModel): The full set of updated values.
        password_db (PasswordsFirestoreClient): The passwords database client.
        user (User): The authenticated user resolved from the request.
        dek (bytes): The authenticated user's data encryption key.

    Returns:
        PasswordGetResponseModel: The updated password.

    Raises:
        HTTPException: If the password is not found or is marked as deleted
            (HTTP 404), or an unexpected Firestore error occurs (HTTP 500).

    """
    password_dao = PasswordDAO(password_db, dek=dek)

    try:
        current = await get_owned_password(password_dao, password_id, user)
        if current.deleted_at is not None:
            raise NotFound(f"Password {password_id} not found")
        password = await password_dao.update(
            str(password_id),
            **body.model_dump(exclude={"fields"}),
            fields=build_fields(body.fields),
        )
    except NotFound as e:
        logger.warning("Password not found", password_id=str(password_id))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Password not found") from e
    except GoogleAPICallError as e:
        logger.exception("Error updating password")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
        ) from e

    return PasswordGetResponseModel.model_validate(password)


@router.patch("/{password_id}", response_model=PasswordGetResponseModel, description="Patch a password by ID")
async def patch_password(
    password_id: Annotated[UUID, Path(description="The unique identifier of the password to update")],
    body: Annotated[PasswordPatchRequestModel, Body(description="The request body for updating a password")],
    password_db: Annotated[PasswordsFirestoreClient, Depends(get_password_db)],
    user: Annotated[User, Depends(authorize_user)],
    dek: Annotated[bytes, Depends(get_user_dek)],
) -> PasswordGetResponseModel:
    """Update a password partially by its ID for the authenticated user.

    Only the fields explicitly provided in the request body are updated. If
    ``fields`` is provided, it replaces the existing password fields.

    Args:
        password_id (UUID): The unique identifier of the password to update.
        body (PasswordPatchRequestModel): The subset of values to update.
        password_db (PasswordsFirestoreClient): The passwords database client.
        user (User): The authenticated user resolved from the request.
        dek (bytes): The authenticated user's data encryption key.

    Returns:
        PasswordGetResponseModel: The updated password.

    Raises:
        HTTPException: If the password is not found or is marked as deleted
            (HTTP 404), or an unexpected Firestore error occurs (HTTP 500).

    """
    password_dao = PasswordDAO(password_db, dek=dek)

    try:
        current = await get_owned_password(password_dao, password_id, user)
        if current.deleted_at is not None:
            raise NotFound(f"Password {password_id} not found")
        changes = body.model_dump(exclude_unset=True, exclude={"fields"})
        if body.fields is not None:
            changes["fields"] = build_fields(body.fields)
        password = await password_dao.update(str(password_id), **changes)
    except NotFound as e:
        logger.warning("Password not found", password_id=str(password_id))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Password not found") from e
    except GoogleAPICallError as e:
        logger.exception("Error updating password")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
        ) from e

    return PasswordGetResponseModel.model_validate(password)


@router.delete("/{password_id}", status_code=status.HTTP_204_NO_CONTENT, description="Delete a password by ID")
async def delete_password(
    password_id: Annotated[UUID, Path(description="The unique identifier of the password to delete")],
    password_db: Annotated[PasswordsFirestoreClient, Depends(get_password_db)],
    user: Annotated[User, Depends(authorize_user)],
) -> None:
    """Delete a password by its ID for the authenticated user.

    The password is marked as deleted rather than removed from Firestore.

    Args:
        password_id (UUID): The unique identifier of the password to delete.
        password_db (PasswordsFirestoreClient): The passwords database client.
        user (User): The authenticated user resolved from the request.

    Returns:
        None.

    Raises:
        HTTPException: If the password is not found (HTTP 404) or an
            unexpected Firestore error occurs (HTTP 500).

    """
    password_dao = PasswordDAO(password_db)

    try:
        await get_owned_password(password_dao, password_id, user)
        await password_dao.mark_as_deleted(str(password_id))
    except NotFound as e:
        logger.warning("Password not found", password_id=str(password_id))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Password not found") from e
    except GoogleAPICallError as e:
        logger.exception("Error deleting password")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
        ) from e
