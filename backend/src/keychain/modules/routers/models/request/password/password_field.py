"""Request models for fields embedded in a password document."""

__all__ = ("PasswordFieldCreate", "PasswordFieldValueCreate")

from datetime import datetime

from pydantic import Field

from keychain.modules.routers.models.base.request import BaseRequestModel


class PasswordFieldValueCreate(BaseRequestModel):
    """Request model for a value created together with a password field."""

    value: str = Field(..., description="The value of the field")


class PasswordFieldCreate(BaseRequestModel):
    """Request model for a field created together with a password."""

    name: str = Field(..., description="The name of the field", min_length=1)
    values: list[PasswordFieldValueCreate] = Field(
        ...,
        description="The values of the field; their order in the list is preserved",
        min_length=1,
    )
    deleted_at: datetime | None = Field(
        None,
        description="When the field was deleted; send the existing timestamp to keep a field deleted, "
        "or null for an active field",
    )
