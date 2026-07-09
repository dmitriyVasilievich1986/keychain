"""Application lifespan management for initializing and tearing down services."""

__all__ = ["lifespan"]

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from loguru import logger

from keychain.config import AppConfig
from keychain.services.cryptography.client import CryptographyClient
from keychain.services.db_client.client import DBClient


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
    logger.info(f"Debug mode: {app.debug}")

    # Initialize services
    logger.info("Initializing Application services...")
    app_config = AppConfig.get_or_create()
    db_client = DBClient(app_config)
    logger.info("Database client initialized successfully.")

    CryptographyClient(config=app_config)
    logger.info("Cryptography client initialized successfully.")

    yield

    # Cleanup
    logger.info("Shutting down application lifespan...")
    await db_client.close()
    logger.info("Database client closed successfully.")
