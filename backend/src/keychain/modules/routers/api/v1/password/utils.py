"""Helpers shared by the API v1 password routes."""

__all__ = ("build_fields", "get_owned_password")

from uuid import UUID

from google.api_core.exceptions import NotFound

from keychain.modules.routers.models.request.password import PasswordFieldCreate
from keychain.services.daos.firestore import PasswordDAO
from keychain.services.daos.firestore.models import Field, FieldValue, Password, User


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
            in the list defines their position; a field's ``deleted_at`` is kept,
            so deleted fields stay soft-deleted.

    Returns:
        list[Field]: The Firestore field models.

    """
    return [
        Field(
            name=field.name,
            position=position,
            values=[FieldValue(value=field_value.value) for field_value in field.values],
            deleted_at=field.deleted_at,
        )
        for position, field in enumerate(fields)
    ]
