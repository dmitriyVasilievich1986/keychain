from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FieldRepresentation(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    name: str = Field(..., description="The name of the field")
    value: str = Field(..., description="The value of the field")
    created_at: datetime = Field(
        ..., description="The creation timestamp of the field", default=datetime.now
    )
    is_deleted: bool = Field(False, description="Indicates if the field is deleted")


class PasswordRepresentation(BaseModel):
    id: int = Field(..., description="The unique identifier of the password")
    name: str = Field(..., description="The name of the password entry")
    image_url: str = Field(
        ..., description="The URL of the image associated with the password entry"
    )
    fields: list[FieldRepresentation] = Field(
        ...,
        description="A list of fields associated with the password entry",
        default_factory=list,
    )
