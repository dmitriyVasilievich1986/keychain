from datetime import datetime
from typing import Any

import sqlalchemy as sa
from flask import g
from flask_appbuilder import Model
from flask_appbuilder.security.sqla.models import User
from sqlalchemy.orm import Mapped, relationship

from keychain.models.fields import Field
from keychain.models.types import PasswordRepresentation


class Password(Model):
    __tablename__ = "password"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, unique=False, nullable=False)
    created_at = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)
    image_url = sa.Column(
        sa.String(256), nullable=True, default="/static/i/no-photo.png"
    )
    fields: Mapped[list[Field]] = relationship(
        Field, cascade="all, delete-orphan", backref="password"
    )
    user_id = sa.Column(sa.Integer, sa.ForeignKey(User.id), nullable=False)

    def __init__(self, **kwargs: Any) -> None:
        kwargs["user_id"] = g.user.id
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        """
        Returns a string representation of the object.
        """

        return self.serialize().model_dump_json()

    def serialize(self) -> PasswordRepresentation:
        """
        Generate a JSON representation of the model.

        Returns:
            PasswordRepresentation: A dictionary representing the model in JSON format.
        """

        return PasswordRepresentation.model_validate(self)
