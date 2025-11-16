"""Models for all routers."""

from .request import (
    PasswordCreateRequestModel,
    PasswordUpdateRequestModel,
    UserCreateRequestModel,
    UserUpdateRequestModel,
)
from .response import (
    PasswordGetResponseModel,
    PasswordGetResponseModelSimple,
    UserGetResponseModel,
    UserGetResponseModelSimple,
)

__all__ = [
    "PasswordCreateRequestModel",
    "PasswordGetResponseModel",
    "PasswordGetResponseModelSimple",
    "PasswordUpdateRequestModel",
    "UserCreateRequestModel",
    "UserGetResponseModel",
    "UserGetResponseModelSimple",
    "UserUpdateRequestModel",
]
