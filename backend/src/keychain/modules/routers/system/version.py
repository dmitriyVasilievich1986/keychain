"""Version API router."""

__all__ = ["router"]

from typing import Annotated

from fastapi import APIRouter, status
from fastapi.params import Depends

from keychain.config import AppConfig
from keychain.modules.middlewares.dependencies import get_config
from keychain.modules.routers.models.response.system import VersionResponse

router = APIRouter()


@router.get(
    "/version",
    response_model=VersionResponse,
    status_code=status.HTTP_200_OK,
    summary="Service Version",
)
async def get_version(
    config: Annotated[AppConfig, Depends(get_config)],
) -> VersionResponse:
    """Asynchronously retrieves the current service version.

    Returns:
        VersionResponse: An object containing the current version of the service.

    """
    return VersionResponse(version=config.info.version)
