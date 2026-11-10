"""Logging of the local API documentation URLs."""

__all__ = ("log_docs_urls",)

import structlog
from fastapi import FastAPI

logger = structlog.stdlib.get_logger(__name__)


def log_docs_urls(app: FastAPI, port: int) -> None:
    """Log local URLs of the interactive API docs and the OpenAPI schema.

    Docs that are disabled on the application (their URL is ``None``) are skipped.

    Args:
        app: The configured FastAPI application.
        port: The port the application server listens on.

    """
    base_url = f"http://localhost:{port}{app.root_path}"
    docs = (
        ("Swagger UI", app.docs_url),
        ("ReDoc", app.redoc_url),
        ("OpenAPI schema", app.openapi_url),
    )
    for name, path in docs:
        if path:
            logger.debug(f"{name} available", url=f"{base_url}{path}")
