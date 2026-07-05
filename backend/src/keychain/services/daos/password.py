"""Data access object for password records."""

__all__ = ["PasswordDAO"]

from keychain.services.db_client.models.password import Password

from .base import BaseDAO


class PasswordDAO(BaseDAO[Password]):
    """Provide database access operations for :class:`Password` records."""

    pk_column_name: str = "id"
    database_model: type[Password] = Password

    get_all_columns = (Password.id, Password.name, Password.image_url)
    select_in_options_single = (Password.fields,)
