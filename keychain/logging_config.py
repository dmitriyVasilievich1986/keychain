import logging
import sys

from keychain.config.base import Config


def setup_logging(config: Config) -> None:
    """
    Configures the root logger using the provided configuration.
    Sets the logging level and attaches a stream handler that outputs log messages
    to standard output. The log messages are formatted to include the timestamp,
    log level, and message.

    Args:
        config (Config): A configuration object or dictionary containing the "LOG_LEVEL" key
            which specifies the desired logging level (e.g., "DEBUG", "INFO", "WARNING", etc.).

    Returns:
        None
    """

    logger = logging.getLogger()
    logger.setLevel(config.LOG_LEVEL)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(config.LOG_LEVEL)
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
