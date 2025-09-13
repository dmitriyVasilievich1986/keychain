from datetime import datetime
from typing import Any, TYPE_CHECKING

import sqlalchemy as sa
from flask import current_app
from flask_appbuilder import Model

from keychain.models.types import FieldRepresentation

if TYPE_CHECKING:
    from keychain.app import PasswordApp

    current_app: PasswordApp  # type: ignore[no-redef]


class Field(Model):
    __tablename__ = "field"

    name = sa.Column(sa.String, nullable=False)
    id = sa.Column(sa.Integer, primary_key=True)
    value = sa.Column(sa.String, nullable=False)
    is_deleted = sa.Column(sa.Boolean, default=False)
    created_at = sa.Column(sa.DateTime, nullable=False, default=datetime.now)
    password_id = sa.Column(sa.Integer, sa.ForeignKey("password.id"), nullable=False)

    def __init__(self, *, value: str, **kwargs: Any) -> None:
        value = current_app.fernet.encrypt(str(value).encode()).decode()
        super().__init__(value=value, **kwargs)

    def __repr__(self) -> str:
        """Returns a string representation of the object.

        Returns:
            str: A JSON string representation of the object.
        """

        return self.serialize().model_dump_json()

    @property
    def get_value(self) -> str:
        """
        Decrypts and decodes the value of the keychain entry.

        Returns:
            str: The decrypted and decoded value.
        """

        return current_app.fernet.decrypt(self.value.encode()).decode()

    def check(self, value: str) -> bool:
        """
        Check if the given value matches the stored value.

        Parameters:
            value (str): The value to be checked.

        Returns:
            bool: True if the given value matches the stored value,
                False otherwise.
        """

        return self.get_value == value

    def serialize(self) -> FieldRepresentation:
        """
        Returns a dictionary representation of the model object.

        Returns:
            FieldRepresentation: A dictionary containing the name, value,
                is_deleted, and created_at attributes.
        """

        return FieldRepresentation.model_validate(self)
