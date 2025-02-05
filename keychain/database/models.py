import json
from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from flask import current_app, g
from flask_appbuilder import Model
from flask_appbuilder.security.sqla.models import User
from sqlalchemy.orm import Mapped, relationship

if TYPE_CHECKING:
    pass


class Field(Model):
    __tablename__ = "field"

    name = sa.Column(sa.String, nullable=False)
    id = sa.Column(sa.Integer, primary_key=True)
    value = sa.Column(sa.String, nullable=False)
    is_deleted = sa.Column(sa.Boolean, default=False)
    created_at = sa.Column(sa.DateTime, nullable=False, default=datetime.now)
    password_id = sa.Column(sa.Integer, sa.ForeignKey("password.id"), nullable=False)

    def __init__(self, *, value: str, **kwargs) -> None:
        value = current_app.fernet.encrypt(str(value).encode()).decode()
        super().__init__(value=value, **kwargs)

    def __repr__(self) -> str:
        """Returns a string representation of the object.

        Returns:
            str: A JSON string representation of the object.
        """

        return json.dumps(self.json())

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

    def json(self) -> dict:
        """
        Returns a dictionary representation of the model object.

        Returns:
            dict: A dictionary containing the name, value,
                is_deleted, and created_at attributes.
        """

        return {
            "name": self.name,
            "value": self.get_value,
            "is_deleted": self.is_deleted,
            "created_at": str(self.created_at.replace(microsecond=0)),
        }


class Password(Model):
    __tablename__ = "password"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, unique=False, nullable=False)
    created_at = sa.Column(sa.DateTime, nullable=False, default=datetime.now)
    image_url = sa.Column(
        sa.String(256), nullable=True, default="/static/i/no-photo.png"
    )
    fields: Mapped[list[Field]] = relationship(
        Field, cascade="all, delete-orphan", backref="password"
    )
    user_id = sa.Column(sa.Integer, sa.ForeignKey(User.id), nullable=False)

    def __init__(self, **kwargs) -> None:
        kwargs["user_id"] = g.user.id
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        """
        Returns a string representation of the object.
        """

        return json.dumps(self.json())

    def json(self) -> dict:
        """
        Generate a JSON representation of the model.

        Returns:
            dict: A dictionary representing the model in JSON format.
        """

        fields = sorted(
            [x.json() for x in self.fields], key=lambda x: x["created_at"], reverse=True
        )
        return {
            "id": self.id,
            "fields": fields,
            "name": self.name,
            "image_url": self.image_url,
        }
