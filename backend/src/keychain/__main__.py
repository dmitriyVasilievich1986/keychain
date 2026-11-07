"""Application entrypoint for running the keychain backend with uvicorn."""

import uvicorn

from keychain.config.app_config import AppConfig
from keychain.modules.app import get_app
from keychain.utils import configure_logging


def main() -> None:
    """Configure logging, build the app from config and run it with uvicorn."""
    config = AppConfig.get_or_create()
    configure_logging(
        log_level=config.info.logs.log_level,
        service=config.info.name,
        version=config.info.version,
        logs_folder_path=config.info.logs.logs_folder_path,
        is_simple_output=config.info.logs.is_simple_output,
    )

    app = get_app(config=config)

    uvicorn.run(
        app,
        host=config.info.host,
        port=config.info.port,
        log_config=None,
    )


if __name__ == "__main__":
    main()
