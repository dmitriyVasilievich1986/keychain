"""System health check router."""

__all__ = ("router",)

import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from keychain.modules.middlewares.dependencies import get_password_db, get_users_db
from keychain.modules.routers.models.response.system import (
    HealthResponse,
    ServiceHealth,
)
from keychain.services.db_client.firestore import PasswordsFirestoreClient, UsersFirestoreClient

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
    users_db: Annotated[UsersFirestoreClient, Depends(get_users_db)],
    password_db: Annotated[PasswordsFirestoreClient, Depends(get_password_db)],
) -> Response:
    """Report service health based on connectivity to both Firestore databases.

    Args:
        users_db (UsersFirestoreClient): The users database client.
        password_db (PasswordsFirestoreClient): The passwords database client.

    Returns:
        Response: 200 if every service is up, otherwise 503.

    """
    clients = (users_db, password_db)
    results = await asyncio.gather(*(client.healthcheck() for client in clients))
    services = [
        ServiceHealth(
            name="firestore",
            status="UP" if is_up else "DOWN",
            extra={"db": client.db_name, "collection": client.collection_name},
        )
        for client, is_up in zip(clients, results, strict=True)
    ]
    is_down = any(service.status == "DOWN" for service in services)

    return Response(
        status_code=status.HTTP_200_OK if not is_down else status.HTTP_503_SERVICE_UNAVAILABLE,
        content=HealthResponse(status="UP" if not is_down else "DOWN", services=services).model_dump_json(),
        headers={"Content-Type": "application/json"},
    )
