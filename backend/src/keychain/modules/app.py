"""FastAPI application factory module.

This module provides the main application factory function for creating
and configuring the FastAPI application instance with all necessary
routers, middleware, and lifecycle management.
"""

__all__ = ["get_app"]

from fastapi import APIRouter, FastAPI
from loguru import logger

from keychain.config import AppConfig
from keychain.modules.middlewares import lifespan
from keychain.modules.routers.api import router as api_router


def get_app(config: AppConfig | None = None) -> FastAPI:
    """Create and configure a FastAPI application instance.

    This function initializes a FastAPI application with the provided
    configuration, sets up the application metadata (title, description,
    version), configures debug mode, attaches the lifespan context manager,
    and includes all API routers.

    Args:
        config: Optional application configuration. If not provided, the
            default configuration will be loaded using AppConfig.get_or_create().

    Returns:
        FastAPI: A fully configured FastAPI application instance with all
            routers and middleware attached.

    """
    config = config or AppConfig.get_or_create()
    logger.debug(f"Config: {config}")

    app = FastAPI(
        title=config.info.name,
        description=config.info.description,
        version=config.info.version,
        debug=config.info.debug,
        lifespan=lifespan,
    )

    app_router = APIRouter()
    app_router.include_router(api_router)

    app.include_router(app_router)

    return app
