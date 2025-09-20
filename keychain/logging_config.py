import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from keychain.config.base import Config


def setup_logging(config: "Config") -> None:
    """Configures logging for the application using the loguru library.

    Removes any existing loguru handlers and adds new ones:
    - Logs to stdout and stderr at the level specified in the config.
    - Logs to a file with rotation every 10 MB and retention for 10 days.

    Args:
        config (Config): Configuration object containing logging settings such as LOG_LEVEL and LOG_FILE.

    """
    from loguru import logger

    logger.remove()
    logger.add(sys.stdout, level=config.LOG_LEVEL)
    logger.add(sys.stderr, level=config.LOG_LEVEL)
    logger.add(config.LOG_FILE, rotation="10 MB", retention="10 days", level=config.LOG_LEVEL)
