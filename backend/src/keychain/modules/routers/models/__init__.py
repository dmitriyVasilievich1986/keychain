"""Models for all routers."""

from .request import (
    FieldCreateRequestModel,
    FieldUpdateRequestModel,
    PasswordCreateRequestModel,
    PasswordUpdateRequestModel,
    UserCreateRequestModel,
    UserUpdateRequestModel,
)
from .response import (
    ErrorResponse,
    FieldGetResponseModel,
    FieldGetResponseModelSimple,
    HealthResponse,
    PasswordGetResponseModel,
    PasswordGetResponseModelSimple,
    UserGetResponseModel,
    UserGetResponseModelSimple,
    VersionResponse,
)

__all__ = [
    "ErrorResponse",
    "FieldCreateRequestModel",
    "FieldGetResponseModel",
    "FieldGetResponseModelSimple",
    "FieldUpdateRequestModel",
    "HealthResponse",
    "PasswordCreateRequestModel",
    "PasswordGetResponseModel",
    "PasswordGetResponseModelSimple",
    "PasswordUpdateRequestModel",
    "UserCreateRequestModel",
    "UserGetResponseModel",
    "UserGetResponseModelSimple",
    "UserUpdateRequestModel",
    "VersionResponse",
]
