"""Application entrypoint for running the keychain backend with uvicorn."""

import uvicorn

from keychain.config.app_config import AppConfig
from keychain.modules.app import get_app


def main() -> None:
    """Build the app from config and run it with uvicorn."""
    config = AppConfig.get_or_create()

    app = get_app(config=config)

    uvicorn.run(
        app,
        host=config.info.host,
        port=config.info.port,
        log_level=config.info.log_level.lower(),
    )


if __name__ == "__main__":
    main()
