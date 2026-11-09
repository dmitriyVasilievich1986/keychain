"""Structlog configuration producing Google Cloud Logging compatible output."""

__all__ = ("LOG_FILES_MAX_COUNT", "configure_logging")

import logging
import sys
from logging.handlers import TimedRotatingFileHandler

import structlog
from structlog.typing import EventDict, Processor, WrappedLogger
from structlog_gcp import error_reporting, processors as gcp_processors

from keychain.config.models.info.logs import Logs

LOG_FILES_MAX_COUNT = 5
"""Maximum number of log files kept in the logs folder (the active file included)."""

_CALLSITE_ADDER = structlog.processors.CallsiteParameterAdder(
    parameters=[
        structlog.processors.CallsiteParameter.PATHNAME,
        structlog.processors.CallsiteParameter.MODULE,
        structlog.processors.CallsiteParameter.FUNC_NAME,
        structlog.processors.CallsiteParameter.LINENO,
    ],
)
_CALLSITE_KEYS = ("pathname", "module", "func_name", "lineno")


def _drop_callsite(_logger: WrappedLogger, _method_name: str, event_dict: EventDict) -> EventDict:
    """Remove call-site fields that are only needed for the GCP source location.

    Args:
        _logger: The wrapped logger instance (unused).
        _method_name: The name of the called log method (unused).
        event_dict: The structlog event dictionary.

    Returns:
        EventDict: The event dictionary without call-site fields.

    """
    for key in _CALLSITE_KEYS:
        event_dict.pop(key, None)
    return event_dict


def _drop_color_message(_logger: WrappedLogger, _method_name: str, event_dict: EventDict) -> EventDict:
    """Remove the ANSI-colored duplicate of the message that uvicorn adds as an ``extra`` field.

    Args:
        _logger: The wrapped logger instance (unused).
        _method_name: The name of the called log method (unused).
        event_dict: The structlog event dictionary.

    Returns:
        EventDict: The event dictionary without the ``color_message`` field.

    """
    event_dict.pop("color_message", None)
    return event_dict


def _build_gcp_formatter(
    pre_chain: list[Processor],
    service: str | None,
    version: str | None,
) -> structlog.stdlib.ProcessorFormatter:
    """Build a formatter rendering records as GCP structured JSON lines.

    The processors mirror ``structlog_gcp.build_gcp_processors`` except for the call-site
    lookup: it is done once, before the record reaches the formatter, because inside a
    formatter the stack no longer points at the code that emitted the log.

    Args:
        pre_chain: Processors applied to records coming from the standard library ``logging``.
        service: Service name reported to Google Cloud Error Reporting.
        version: Service version reported to Google Cloud Error Reporting.

    Returns:
        structlog.stdlib.ProcessorFormatter: The configured formatter.

    """
    return structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=[*pre_chain, _CALLSITE_ADDER],
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            gcp_processors.init_cloud_logging,
            gcp_processors.LogSeverity(),
            gcp_processors.code_location,
            *error_reporting.setup_exceptions(),
            error_reporting.ReportError(["CRITICAL"]),
            error_reporting.ServiceContext(service, version),
            gcp_processors.finalize_cloud_logging,
            structlog.processors.JSONRenderer(),
        ],
    )


def _build_simple_formatter(pre_chain: list[Processor]) -> structlog.stdlib.ProcessorFormatter:
    """Build a formatter rendering records as human-readable lines for local development.

    Args:
        pre_chain: Processors applied to records coming from the standard library ``logging``.

    Returns:
        structlog.stdlib.ProcessorFormatter: The configured formatter.

    """
    return structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=pre_chain,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            _drop_callsite,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.stdlib.add_log_level,
            structlog.dev.ConsoleRenderer(colors=sys.stderr.isatty()),
        ],
    )


def configure_logging(
    logs: Logs,
    service: str | None = None,
    version: str | None = None,
) -> None:
    """Configure structlog and the standard library ``logging`` to emit GCP structured logs.

    Logs are always written to the terminal (``stderr``). Records from the standard
    library ``logging`` module (e.g. third-party libraries) are rendered the same way
    as structlog records. Calling this function again replaces the previous configuration.

    When ``logs.logs_folder_path`` is set, logs are additionally written to that folder in
    the GCP JSON format. The log file is rotated at midnight (UTC), one file per day,
    and at most ``LOG_FILES_MAX_COUNT`` files are kept; older files are removed.

    When ``logs.is_simple_output`` is set, the terminal output is rendered as human-readable
    lines instead of GCP JSON. It is intended for local development; file logs are always
    written in the GCP JSON format.

    Args:
        logs: Logs configuration (log level, simple output flag and logs folder).
        service: Service name reported to Google Cloud Error Reporting.
        version: Service version reported to Google Cloud Error Reporting.

    """
    pre_chain: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.ExtraAdder(),
        _drop_color_message,
    ]

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(
        _build_simple_formatter(pre_chain)
        if logs.is_simple_output
        else _build_gcp_formatter(pre_chain, service, version),
    )
    handlers: list[logging.Handler] = [console_handler]

    if logs.logs_folder_path is not None:
        logs.logs_folder_path.mkdir(parents=True, exist_ok=True)
        file_handler = TimedRotatingFileHandler(
            logs.logs_folder_path / f"{service or 'app'}.log",
            when="midnight",
            backupCount=LOG_FILES_MAX_COUNT - 1,
            encoding="utf-8",
            utc=True,
        )
        file_handler.setFormatter(_build_gcp_formatter(pre_chain, service, version))
        handlers.append(file_handler)

    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        handler.close()
    for handler in handlers:
        root_logger.addHandler(handler)
    root_logger.setLevel(logs.log_level)

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.contextvars.merge_contextvars,
            _CALLSITE_ADDER,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
