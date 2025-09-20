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
    image_url = sa.Column(sa.String(256), nullable=True, default="/static/i/no-photo.png")
    fields: Mapped[list[Field]] = relationship(Field, cascade="all, delete-orphan", backref="password")
    user_id = sa.Column(sa.Integer, sa.ForeignKey(User.id), nullable=False)

    def __init__(self, **kwargs: Any) -> None:
        """Initializes a new instance of the class.

        Initializes a new instance of the class, automatically setting the 'user_id' field
        to the current user's ID from the Flask global context (`g.user.id`), and passes
        all keyword arguments to the superclass initializer.

        Args:
            **kwargs (Any): Arbitrary keyword arguments for model initialization.

        Raises:
            AttributeError: If `g.user` or `g.user.id` is not available in the context.

        """
        kwargs["user_id"] = g.user.id
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        """Returns a JSON string representation of the serialized model instance.

        This method calls the `serialize()` method on the instance and then
        dumps the resulting model to a JSON string using `model_dump_json()`.

        Returns:
            str: JSON string representation of the model.

        """
        return self.serialize().model_dump_json()

    def serialize(self) -> PasswordRepresentation:
        """Generate a JSON representation of the model.

        Returns:
            PasswordRepresentation: A dictionary representing the model in JSON format.

        """
        return PasswordRepresentation.model_validate(self)
