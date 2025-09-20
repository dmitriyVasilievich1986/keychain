from logging import getLogger

from marshmallow import fields, Schema

logger = getLogger(__name__)


class HealthResponse(Schema):
    status = fields.Str(default="ok")


class VersionResponse(Schema):
    version = fields.Str()
