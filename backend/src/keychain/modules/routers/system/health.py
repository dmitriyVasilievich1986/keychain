"""System health check router."""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from keychain.modules.middlewares.dependencies import get_firestore
from keychain.modules.routers.models.response.system import (
    HealthResponse,
    ServiceHealth,
)
from keychain.services.db_client.firestore import FirestoreClient

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
async def health_check(
    firestore: Annotated[FirestoreClient, Depends(get_firestore)],
) -> Response:
    """Report service health based on Firestore connectivity.

    Args:
        firestore (FirestoreClient): The Firestore client used to verify connectivity.

    Returns:
        Response: 200 if every service is up, otherwise 503.

    """
    firestore_up = await firestore.healthcheck()
    services = [
        ServiceHealth(name="firestore", status="UP" if firestore_up else "DOWN"),
    ]
    is_down = any(service.status == "DOWN" for service in services)

    return Response(
        status_code=status.HTTP_200_OK if not is_down else status.HTTP_503_SERVICE_UNAVAILABLE,
        content=HealthResponse(status="UP" if not is_down else "DOWN", services=services).model_dump_json(),
        headers={"Content-Type": "application/json"},
    )
