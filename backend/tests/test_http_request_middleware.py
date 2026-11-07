"""Tests for the HTTP request logging middleware."""

import pytest
import structlog
from starlette.types import Message, Receive, Scope, Send
from structlog.testing import capture_logs

from keychain.modules.middlewares import HTTPRequestMiddleware


def _scope(headers: list[tuple[bytes, bytes]] | None = None) -> Scope:
    """Build a minimal HTTP ASGI scope."""
    return {"type": "http", "path": "/items", "method": "GET", "headers": headers or []}


async def _receive() -> Message:
    """Return an empty HTTP request body message."""
    return {"type": "http.request", "body": b"", "more_body": False}


async def _call(app: HTTPRequestMiddleware, scope: Scope) -> list[Message]:
    """Run the middleware and return the messages sent to the client."""
    sent: list[Message] = []

    async def send(message: Message) -> None:
        sent.append(message)

    await app(scope, _receive, send)
    return sent


async def _ok_app(_scope: Scope, _receive: Receive, send: Send) -> None:
    """Respond with 200 and the bound request id in the body."""
    request_id = structlog.contextvars.get_contextvars()["request_id"]
    await send({"type": "http.response.start", "status": 200, "headers": []})
    await send({"type": "http.response.body", "body": request_id.encode()})


async def test_binds_context_vars_during_request() -> None:
    """Context vars should hold request_id, path and method while the request runs."""
    seen: dict[str, object] = {}

    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        seen.update(structlog.contextvars.get_contextvars())
        await _ok_app(scope, receive, send)

    await _call(HTTPRequestMiddleware(app), _scope())

    assert seen["path"] == "/items"
    assert seen["method"] == "GET"
    assert seen["request_id"]
    assert structlog.contextvars.get_contextvars() == {}


async def test_logs_request_run_time() -> None:
    """A completion log with status code and duration should be emitted."""
    with capture_logs() as logs:
        await _call(HTTPRequestMiddleware(_ok_app), _scope())

    assert logs[-1]["event"] == "Request completed"
    assert logs[-1]["status_code"] == 200
    assert logs[-1]["duration_ms"] >= 0


async def test_reuses_valid_incoming_request_id() -> None:
    """A well-formed incoming X-Request-ID should be reused and returned."""
    sent = await _call(HTTPRequestMiddleware(_ok_app), _scope([(b"x-request-id", b"abc-123")]))

    assert sent[1]["body"] == b"abc-123"
    assert (b"x-request-id", b"abc-123") in sent[0]["headers"]


async def test_replaces_malformed_incoming_request_id() -> None:
    """A malformed incoming X-Request-ID should be replaced with a generated one."""
    sent = await _call(HTTPRequestMiddleware(_ok_app), _scope([(b"x-request-id", b"bad id\n")]))

    assert sent[1]["body"] not in (b"", b"bad id\n")


async def test_logs_and_reraises_exceptions() -> None:
    """Exceptions from the app should be logged with the run time and re-raised."""

    async def failing_app(_scope: Scope, _receive: Receive, _send: Send) -> None:
        raise RuntimeError("boom")

    with capture_logs() as logs, pytest.raises(RuntimeError):
        await _call(HTTPRequestMiddleware(failing_app), _scope())

    assert logs[-1]["event"] == "Request failed"
    assert "duration_ms" in logs[-1]


async def test_passes_through_non_http_scopes() -> None:
    """Non-HTTP scopes (e.g. lifespan) should be forwarded untouched."""
    called: list[str] = []

    async def app(scope: Scope, _receive: Receive, _send: Send) -> None:
        called.append(scope["type"])

    async def send(_message: Message) -> None:
        pass

    await HTTPRequestMiddleware(app)({"type": "lifespan"}, _receive, send)

    assert called == ["lifespan"]
