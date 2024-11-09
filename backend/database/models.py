import json
from datetime import datetime

import sqlalchemy as sa
from flask import current_app
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import db


class Password(db.Model):
    __tablename__ = "password"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, unique=True, nullable=False)
    created_at = sa.Column(sa.DateTime, nullable=False, default=datetime.now)
    image_url = sa.Column(
        sa.String(256), nullable=True, default="/static/i/no-photo.png"
    )
    fields: Mapped[list["Field"]] = relationship(cascade="all, delete-orphan")

    def __repr__(self):
        return json.dumps(self.json())

    def json(self):
        fields = sorted(
            [x.json() for x in self.fields], key=lambda x: x["created_at"], reverse=True
        )
        return {
            "id": self.id,
            "fields": fields,
            "name": self.name,
            "image_url": self.image_url,
        }


class Field(db.Model):
    __tablename__ = "field"

    name = sa.Column(sa.String, nullable=False)
    value = sa.Column(sa.BINARY, nullable=False)
    id = sa.Column(sa.Integer, primary_key=True)
    is_deleted = sa.Column(sa.Boolean, default=False)
    password_id = mapped_column(sa.ForeignKey("password.id"))
    created_at = sa.Column(sa.DateTime, nullable=False, default=datetime.now)

    def __init__(self, value: str, *args, **kwargs: dict):
        super().__init__(
            value=current_app.fernet.encrypt(str(value).encode()), **kwargs
        )

    def __repr__(self):
        return json.dumps(self.json())

    @property
    def get_value(self):
        return current_app.fernet.decrypt(self.value).decode()

    def check(self, value):
        return self.get_value == value

    def json(self):
        return {
            "name": self.name,
            "value": self.get_value,
            "is_deleted": self.is_deleted,
            "created_at": str(self.created_at.replace(microsecond=0)),
        }
