"""Application entrypoint for running the keychain backend with uvicorn."""

import uvicorn

from keychain.config.app_config import AppConfig
from keychain.modules.app import get_app
from keychain.utils import configure_logging


def main() -> None:
    """Configure logging, build the app from config and run it with uvicorn."""
    config = AppConfig()
    configure_logging(config.info.logs, service=config.info.name, version=config.info.version)

    app = get_app(config=config)

    uvicorn.run(
        app,
        host=config.info.host,
        port=config.info.port,
        log_config=None,
    )


if __name__ == "__main__":
    main()
