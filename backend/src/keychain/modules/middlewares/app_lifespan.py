"""Application lifespan management for initializing and tearing down services."""

__all__ = ("lifespan",)

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI

from keychain.config import AppConfig
from keychain.services.db_client.client import DBClient

logger = structlog.stdlib.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage startup and shutdown of application services.

    Initializes the database and cryptography clients on startup, yields
    control while the application runs, and closes the database client on
    shutdown.

    Args:
        app (FastAPI): The FastAPI application instance being started.

    Yields:
        None: Control is yielded back to the application while it runs.

    """
    logger.info("Starting application lifespan...")
    logger.info("Debug mode", debug=app.debug)

    # Initialize services
    logger.info("Initializing Application services...")
    app_config = AppConfig()
    db_client = DBClient(app_config.db.postgresql, app_config.info.debug)
    logger.info("Database client initialized successfully.")

    yield

    # Cleanup
    logger.info("Shutting down application lifespan...")
    await db_client.close()
    logger.info("Database client closed successfully.")
