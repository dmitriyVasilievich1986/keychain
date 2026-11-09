"""System health check router."""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from keychain.modules.middlewares.dependencies import get_db
from keychain.modules.routers.models.response.system import (
    HealthResponse,
    ServiceHealth,
)
from keychain.services.db_client.client import DBClient

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    responses={
        status.HTTP_200_OK: {
            "model": HealthResponse,
            "description": "Service is healthy and connected to dependencies.",
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": HealthResponse,
            "description": "Service is unhealthy.",
        },
    },
)
async def health_check(db: Annotated[DBClient, Depends(get_db)]) -> Response:
    """Report service health based on database connectivity.

    Args:
        db (DBClient): The database client used to verify connectivity.

    Returns:
        Response: A response indicating the service is healthy.

    Raises:
        HTTPException: 503 if the database health check fails.

    """
    services: list[ServiceHealth] = []
    services.append(ServiceHealth(name="postgres", status="UP" if await db.healthcheck() else "DOWN"))
    is_healthy = any(service.status == "DOWN" for service in services)

    return Response(
        status_code=status.HTTP_200_OK if not is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
        content=HealthResponse(status="UP" if not is_healthy else "DOWN", services=services).model_dump_json(),
        headers={"Content-Type": "application/json"},
    )
