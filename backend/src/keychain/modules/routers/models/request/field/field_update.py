"""Field update request model."""

__all__ = ["FieldUpdateRequestModel"]

from pydantic import Field

from keychain.modules.routers.models.base.request import BaseRequestModel


class FieldUpdateRequestModel(BaseRequestModel):
    """Field update request model."""

    value: str = Field(..., description="The value of the field", min_length=1)
