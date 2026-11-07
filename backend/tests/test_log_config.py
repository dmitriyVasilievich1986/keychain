"""Tests for the structlog GCP logging configuration."""

import json
import logging
from collections.abc import Generator
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

import pytest
import structlog
from pydantic import ValidationError

from keychain.config.models.info.logs import Logs
from keychain.utils import configure_logging
from keychain.utils.log_config import LOG_FILES_MAX_COUNT


@pytest.fixture(autouse=True)
def _restore_logging() -> Generator[None]:
    """Restore the root logger handlers and structlog defaults after each test."""
    root_logger = logging.getLogger()
    handlers, level = root_logger.handlers[:], root_logger.level
    yield
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        handler.close()
    for handler in handlers:
        root_logger.addHandler(handler)
    root_logger.setLevel(level)
    structlog.reset_defaults()


def _file_handler() -> TimedRotatingFileHandler:
    """Return the rotating file handler attached to the root logger."""
    return next(h for h in logging.getLogger().handlers if isinstance(h, TimedRotatingFileHandler))


def test_file_logs_use_gcp_structure(tmp_path: Path) -> None:
    """Log files should contain GCP structured JSON lines with source location."""
    configure_logging(Logs(log_level="INFO", logs_folder_path=tmp_path), service="keychain", version="1.0")

    structlog.get_logger().debug("hidden")
    structlog.get_logger().info("hello", user_id=1)
    logging.getLogger("third.party").warning("foreign %s", "record")
    _file_handler().flush()

    lines = [json.loads(line) for line in (tmp_path / "keychain.log").read_text().splitlines()]
    assert [line["message"] for line in lines] == ["hello", "foreign record"]
    assert [line["severity"] for line in lines] == ["INFO", "WARNING"]
    assert lines[0]["user_id"] == 1
    assert lines[0]["logging.googleapis.com/sourceLocation"]["function"].endswith(":test_file_logs_use_gcp_structure")


def test_exception_is_reported_as_gcp_error(tmp_path: Path) -> None:
    """Exceptions should be formatted as Google Cloud Error Reporting events."""
    configure_logging(Logs(logs_folder_path=tmp_path), service="keychain", version="1.0")

    try:
        raise ZeroDivisionError("boom")
    except ZeroDivisionError:
        structlog.get_logger().exception("failed")
    _file_handler().flush()

    line = json.loads((tmp_path / "keychain.log").read_text())
    assert line["severity"] == "ERROR"
    assert "ZeroDivisionError: boom" in line["stack_trace"]
    assert line["serviceContext"] == {"service": "keychain", "version": "1.0"}


def test_logs_rotate_daily_and_keep_limited_files(tmp_path: Path) -> None:
    """The log file should rotate daily and keep at most ``LOG_FILES_MAX_COUNT`` files."""
    configure_logging(Logs(logs_folder_path=tmp_path), service="keychain")
    handler = _file_handler()
    assert handler.when == "MIDNIGHT"

    for day in range(1, 10):
        (tmp_path / f"keychain.log.2026-01-0{day}").touch()
    handler.doRollover()

    assert len(list(tmp_path.iterdir())) == LOG_FILES_MAX_COUNT


def test_no_file_logging_without_folder() -> None:
    """Without a logs folder only the terminal handler should be configured."""
    configure_logging(Logs())

    assert not any(isinstance(h, TimedRotatingFileHandler) for h in logging.getLogger().handlers)


def test_simple_output_is_human_readable(capsys: pytest.CaptureFixture[str]) -> None:
    """Simple output should render plain lines instead of JSON."""
    configure_logging(Logs(is_simple_output=True))

    structlog.get_logger().info("hello", user_id=1)

    err = capsys.readouterr().err
    assert "hello" in err
    assert "user_id=1" in err
    assert not err.lstrip().startswith("{")


def test_log_level_must_be_a_known_level() -> None:
    """Unknown log levels should be rejected when the configuration is loaded."""
    with pytest.raises(ValidationError):
        Logs(log_level="VERBOSE")  # ty: ignore[invalid-argument-type]
