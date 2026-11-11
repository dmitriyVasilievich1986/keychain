"""Password patch request model."""

__all__ = ("PasswordPatchRequestModel",)

from pydantic import Field, MISSING

from keychain.modules.routers.models.base.request import BaseRequestModel

from .password_field import PasswordFieldCreate


class PasswordPatchRequestModel(BaseRequestModel):
    """Password patch request model.

    Fields that are not sent stay ``MISSING`` and are left out of
    ``model_dump()``, so only the provided fields are updated. ``name`` and
    ``fields`` cannot be set to null; ``image_url`` can, to remove the image.
    """

    name: str | MISSING = Field(default=MISSING, description="The name of the password", min_length=1)
    image_url: str | MISSING | None = Field(
        default=MISSING, description="The URL of the image associated with the password; null removes it"
    )
    fields: list[PasswordFieldCreate] | MISSING = Field(
        default=MISSING,
        description="The fields of the password; if provided, they replace the existing fields and their order "
        "in the list defines their position",
    )
