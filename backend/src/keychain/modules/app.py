"""FastAPI application factory module.

This module provides the main application factory function for creating
and configuring the FastAPI application instance with all necessary
routers, middleware, and lifecycle management.
"""

__all__ = ("get_app",)

import structlog
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from keychain.config import AppConfig
from keychain.modules.middlewares import HTTPRequestMiddleware, lifespan
from keychain.modules.routers.api import router as api_router
from keychain.modules.routers.system import router as system_router
from keychain.utils import configure_logging

logger = structlog.stdlib.get_logger(__name__)


def get_app(config: AppConfig | None = None) -> FastAPI:
    """Create and configure a FastAPI application instance.

    This function initializes a FastAPI application with the provided
    configuration, configures logging, sets up the application metadata
    (title, description, version), configures debug mode, attaches the
    lifespan context manager, and includes all API routers.

    Args:
        config: Optional application configuration. If not provided, the
            default configuration will be loaded using AppConfig().

    Returns:
        FastAPI: A fully configured FastAPI application instance with all
            routers and middleware attached.

    """
    config = config or AppConfig()
    # Configured here as well as in the CLI: with uvicorn's reloader the app runs in a
    # separate worker process that only calls this factory.
    configure_logging(config.info.logs, service=config.info.name, version=config.info.version)
    logger.debug("Config loaded", config=config.model_dump_json())

    app = FastAPI(
        title=config.info.name,
        description=config.info.description,
        version=config.info.version,
        debug=config.info.debug,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_credentials=config.info.api.allow_credentials,
        allow_origins=config.info.api.allow_origins,
        allow_methods=config.info.api.allow_methods,
        allow_headers=config.info.api.allow_headers,
    )
    # Added last so it is the outermost middleware and measures the full request run time.
    app.add_middleware(HTTPRequestMiddleware)

    app_router = APIRouter(prefix=config.info.api.api_prefix)
    app_router.include_router(api_router)
    app_router.include_router(system_router)

    app.include_router(app_router)

    return app
