import logging
import sys


def setup_logging(config: dict) -> None:
    """
    Set up logging configuration.
    This function configures the root logger to log messages with a level of INFO.
    It adds a StreamHandler to log messages to the standard output.
    The log messages are formatted with a timestamp, log level, and message.
    """

    logger = logging.getLogger()
    logger.setLevel(config["LOG_LEVEL"])

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(config["LOG_LEVEL"])
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
