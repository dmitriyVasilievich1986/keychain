"""System health check router."""

__all__ = ("router",)

import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from keychain.modules.middlewares.dependencies import get_db, get_firestore
from keychain.modules.routers.models.response.system import (
    HealthResponse,
    ServiceHealth,
)
from keychain.services.db_client.client import DBClient
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
    db: Annotated[DBClient, Depends(get_db)],
    firestore: Annotated[FirestoreClient, Depends(get_firestore)],
) -> Response:
    """Report service health based on PostgreSQL and Firestore connectivity.

    Both checks run concurrently, so a slow backend does not delay the other.

    Args:
        db (DBClient): The database client used to verify connectivity.
        firestore (FirestoreClient): The Firestore client used to verify connectivity.

    Returns:
        Response: 200 if every service is up, otherwise 503.

    """
    postgres_up, firestore_up = await asyncio.gather(db.healthcheck(), firestore.healthcheck())
    services = [
        ServiceHealth(name="postgres", status="UP" if postgres_up else "DOWN"),
        ServiceHealth(name="firestore", status="UP" if firestore_up else "DOWN"),
    ]
    is_down = any(service.status == "DOWN" for service in services)

    return Response(
        status_code=status.HTTP_200_OK if not is_down else status.HTTP_503_SERVICE_UNAVAILABLE,
        content=HealthResponse(status="UP" if not is_down else "DOWN", services=services).model_dump_json(),
        headers={"Content-Type": "application/json"},
    )
