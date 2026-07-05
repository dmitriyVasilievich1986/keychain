"""System health check router."""

__all__ = ["router"]

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from keychain.modules.middlewares.dependencies import get_db
from keychain.modules.routers.models.response.system import (
    ErrorResponse,
    HealthResponse,
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
            "model": ErrorResponse,
            "description": "Service is unavailable.",
        },
    },
)
async def health_check(db: Annotated[DBClient, Depends(get_db)]) -> HealthResponse:
    """Report service health based on database connectivity.

    Args:
        db (DBClient): The database client used to verify connectivity.

    Returns:
        HealthResponse: A response indicating the service is healthy.

    Raises:
        HTTPException: 503 if the database health check fails.

    """
    if not await db.healthcheck():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service is unhealthy.")

    return HealthResponse(status="ok")
