"""Application lifespan management for FastAPI."""

__all__ = ["lifespan"]

from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from keychain.config import AppConfig
from keychain.services.db_client.client import DBClient


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    """Manage the application lifecycle, initializing and cleaning up services.

    Args:
        app: The FastAPI application instance.

    Yields:
        None: Control returns to the application during its lifetime.

    Raises:
        ConnectionError: If unable to connect to services.
        Exception: If services fail to initialize.

    """
    logger.info("Starting application lifespan...")
    logger.info(f"Debug mode: {app.debug}")

    # Initialize services
    logger.info("Initializing Application services...")
    app_config = AppConfig.get_or_create()
    db_client = DBClient(app_config)
    await db_client.initialize()
    logger.info("Database client initialized successfully.")

    yield

    # Cleanup
    logger.info("Shutting down application lifespan...")
    await db_client.close()
    logger.info("Database client closed successfully.")
