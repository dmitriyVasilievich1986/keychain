from __future__ import annotations

from logging import getLogger

from flask_appbuilder.api import ModelRestApi
from flask_appbuilder.models.sqla.filters import FilterEqualFunction
from flask_appbuilder.models.sqla.interface import SQLAInterface
from marshmallow import Schema, fields

from keychain.database.models import Password

from .get_user_id import get_user_id

logger = getLogger(__name__)


class FieldGetSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    get_value = fields.Str()
    is_deleted = fields.Bool()
    created_at = fields.DateTime()


class PasswordGetSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    image_url = fields.Str()
    created_at = fields.DateTime()
    fields = fields.Nested(FieldGetSchema, many=True)


class PasswordModelApi(ModelRestApi):
    resource_name = "password"
    datamodel = SQLAInterface(Password)
    allow_browser_login = True
    exclude_route_methods = {"delete"}
    base_filters = [["user_id", FilterEqualFunction, get_user_id]]
    show_model_schema = PasswordGetSchema()
    show_columns = [
        Password.id.key,
        Password.name.key,
        Password.fields.key,
        Password.image_url.key,
        Password.created_at.key,
    ]
    list_columns = [
        Password.id.key,
        Password.name.key,
        Password.image_url.key,
    ]
    add_columns = [
        Password.name.key,
        Password.image_url.key,
    ]
    edit_columns = [
        Password.name.key,
    ]
