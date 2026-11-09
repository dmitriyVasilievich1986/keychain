"""ASGI middleware binding request context to structlog and logging request run time."""

__all__ = ["REQUEST_ID_HEADER", "HTTPRequestMiddleware"]

import re
from time import perf_counter
from typing import cast
from uuid import uuid4

import structlog
from starlette.datastructures import MutableHeaders
from starlette.responses import PlainTextResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

REQUEST_ID_HEADER = "X-Request-ID"
"""Header used to receive and return the request identifier."""

_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,128}$")

logger = structlog.stdlib.get_logger(__name__)


class HTTPRequestMiddleware:
    """Bind ``request_id``, ``path`` and ``method`` to structlog context vars and log request run time.

    The request identifier is taken from the ``X-Request-ID`` request header when it is
    present and well-formed, otherwise a new one is generated. It is returned to the
    client in the ``X-Request-ID`` response header.

    Unhandled exceptions are logged once and answered with a ``500 Internal Server Error``
    response that also carries the ``X-Request-ID`` header.

    The structlog context is cleared at the start and end of every request, so values bound
    while handling a request (e.g. ``user_id``) are included in the completion log but do not
    leak into other requests.
    """

    def __init__(self, app: ASGIApp) -> None:
        """Initialize the middleware.

        Args:
            app: The wrapped ASGI application.

        """
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Handle an ASGI call, logging HTTP requests with their run time.

        Args:
            scope: The ASGI connection scope.
            receive: The ASGI receive callable.
            send: The ASGI send callable.

        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = self._get_request_id(scope)
        status_code = 500
        response_started = False

        async def send_wrapper(message: Message) -> None:
            """Capture the response status code and add the request id header.

            Args:
                message: The ASGI message sent by the application.

            """
            nonlocal status_code, response_started
            if message["type"] == "http.response.start":
                status_code = message["status"]
                response_started = True
                MutableHeaders(scope=message)[REQUEST_ID_HEADER] = request_id
            await send(message)

        # Start from a clean context and clear it afterwards, so values bound further down
        # (e.g. ``user_id`` by ``authorize_user``) never leak into another request.
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id, path=scope["path"], method=scope["method"])
        start = perf_counter()
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            logger.exception("Request failed", status_code=status_code, duration_ms=self._elapsed_ms(start))
            # Answer here rather than re-raising, so the error response carries the request id and
            # the traceback is not logged a second time by Starlette/uvicorn. If the response has
            # already started, nothing more can be sent and the server closes the connection.
            if not response_started:
                await PlainTextResponse("Internal Server Error", status_code=500)(scope, receive, send_wrapper)
        else:
            logger.info("Request completed", status_code=status_code, duration_ms=self._elapsed_ms(start))
        finally:
            structlog.contextvars.clear_contextvars()

    @staticmethod
    def _get_request_id(scope: Scope) -> str:
        """Return the incoming request id if it is well-formed, otherwise generate a new one.

        Args:
            scope: The ASGI connection scope.

        Returns:
            str: The request identifier.

        """
        header = REQUEST_ID_HEADER.lower().encode("latin-1")
        headers_list = cast(list[tuple[bytes, bytes]], scope["headers"])
        for name, value in headers_list:
            if name == header:
                request_id = value.decode("latin-1")
                if _REQUEST_ID_PATTERN.fullmatch(request_id):
                    return request_id
                break
        return uuid4().hex

    @staticmethod
    def _elapsed_ms(start: float) -> float:
        """Return the time elapsed since ``start`` in milliseconds.

        Args:
            start: A ``perf_counter`` timestamp.

        Returns:
            float: Elapsed time in milliseconds, rounded to 3 decimal places.

        """
        return round((perf_counter() - start) * 1000, 3)
