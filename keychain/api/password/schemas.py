from logging import getLogger

from marshmallow import fields, Schema

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
