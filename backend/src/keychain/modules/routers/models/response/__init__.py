"""Response models for all routers."""

from .password import PasswordGetResponseModel, PasswordGetResponseModelSimple
from .user import UserGetResponseModel, UserGetResponseModelSimple

__all__ = [
    "PasswordGetResponseModel",
    "PasswordGetResponseModelSimple",
    "UserGetResponseModel",
    "UserGetResponseModelSimple",
]
