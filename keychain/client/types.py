from pydantic import BaseModel, ConfigDict


class FluidResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
