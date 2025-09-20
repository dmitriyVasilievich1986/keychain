from marshmallow import fields, Schema


class HealthResponse(Schema):
    status = fields.Str(default="ok")


class VersionResponse(Schema):
    version = fields.Str()
