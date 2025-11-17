"""Field create request model."""

__all__ = ["FieldCreateRequestModel"]

from pydantic import Field

from keychain.modules.routers.models.base.request import BaseRequestModel


class FieldCreateRequestModel(BaseRequestModel):
    """Field create request model."""

    name: str = Field(..., description="The name of the field", min_length=1)
    value: str = Field(..., description="The value of the field", min_length=1)
    password_id: int = Field(..., description="The ID of the password that owns the field")
