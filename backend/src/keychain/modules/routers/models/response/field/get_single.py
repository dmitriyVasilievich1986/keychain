"""Field get response model."""

__all__ = ("FieldGetResponseModel",)

from datetime import datetime

from pydantic import Field

from keychain.modules.routers.models.base.response import BaseResponseFromModelSchema


class FieldGetResponseModel(BaseResponseFromModelSchema):
    """Field get response model."""

    id: int = Field(..., description="The ID of the field")
    name: str = Field(..., description="The name of the field")
    value_decrypted: str = Field(..., description="The value of the field")
    is_deleted: bool = Field(..., description="Whether the field is deleted")
    created_at: datetime = Field(..., description="The creation date of the field")
    password_id: int = Field(..., description="The ID of the password that owns the field")
