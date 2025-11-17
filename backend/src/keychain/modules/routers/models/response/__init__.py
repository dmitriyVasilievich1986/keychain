"""Response models for all routers."""

from .field import FieldGetResponseModel, FieldGetResponseModelSimple
from .password import PasswordGetResponseModel, PasswordGetResponseModelSimple
from .system import ErrorResponse, HealthResponse, VersionResponse
from .user import UserGetResponseModel, UserGetResponseModelSimple

__all__ = [
    "ErrorResponse",
    "FieldGetResponseModel",
    "FieldGetResponseModelSimple",
    "HealthResponse",
    "PasswordGetResponseModel",
    "PasswordGetResponseModelSimple",
    "UserGetResponseModel",
    "UserGetResponseModelSimple",
    "VersionResponse",
]
