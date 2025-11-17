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
    FieldGetResponseModel,
    FieldGetResponseModelSimple,
    PasswordGetResponseModel,
    PasswordGetResponseModelSimple,
    UserGetResponseModel,
    UserGetResponseModelSimple,
)

__all__ = [
    "FieldCreateRequestModel",
    "FieldGetResponseModel",
    "FieldGetResponseModelSimple",
    "FieldUpdateRequestModel",
    "PasswordCreateRequestModel",
    "PasswordGetResponseModel",
    "PasswordGetResponseModelSimple",
    "PasswordUpdateRequestModel",
    "UserCreateRequestModel",
    "UserGetResponseModel",
    "UserGetResponseModelSimple",
    "UserUpdateRequestModel",
]
