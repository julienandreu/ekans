"""Logging middleware for HTTP request context."""

import time
from logging import LoggerAdapter, getLogger
from typing import Any, Awaitable, Callable, Dict, MutableMapping

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.middlewares.tracing import get_request_id


class RequestContextAdapter(LoggerAdapter[Any]):
    """Logger adapter that adds request context to log records."""

    def process(
        self, msg: str, kwargs: MutableMapping[str, Any]
    ) -> tuple[str, MutableMapping[str, Any]]:
        """Process the logging message and kwargs.

        Args:
            msg: Log message
            kwargs: Logging kwargs

        Returns:
            tuple: Processed message and kwargs
        """
        kwargs.setdefault("extra", {}).setdefault("extras", {}).update(self.extra)
        return msg, kwargs


class LogMiddleware(BaseHTTPMiddleware):
    """Middleware for adding HTTP context to logs."""

    def __init__(self, app: ASGIApp) -> None:
        """Initialize the middleware.

        Args:
            app: ASGI app
        """
        super().__init__(app)
        self.logger = getLogger("http.request")

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Dispatch the request with logging context.

        Args:
            request: Request
            call_next: Callable[[Request], Awaitable[Response]]

        Returns:
            Response
        """
        start_time = time.time()
        correlation_id = request.headers.get("X-Correlation-ID")

        # Build request context
        context: Dict[str, Any] = {
            "request_id": get_request_id(),
            "correlation_id": correlation_id,
            "http": {
                "request": {
                    "method": request.method,
                    "path": request.url.path,
                    "query": dict(request.query_params),
                    "client_ip": (
                        request.headers.get("X-Forwarded-For", "").split(",")[0]
                        or request.client.host
                        if request.client
                        else None
                    ),
                },
            },
        }

        logger = RequestContextAdapter(self.logger, extra=context)
        logger.info(f"Started {request.method} {request.url.path}")

        try:
            response = await call_next(request)
            duration = round((time.time() - start_time) * 1000, 2)

            # Retrieve request id
            context["request_id"] = response.headers.get("X-Request-ID")

            # Update context with response info
            context["http"].update(
                {
                    "response": {
                        "status_code": response.status_code,
                        "duration_ms": duration,
                    },
                }
            )

            logger = RequestContextAdapter(self.logger, extra=context)
            logger.info(
                f"Completed {request.method} {request.url.path} "
                f"with {response.status_code} in {duration}ms"
            )

            return response

        except Exception as e:
            duration = round((time.time() - start_time) * 1000, 2)
            context["http"].update(
                {
                    "error": {
                        "type": type(e).__name__,
                        "message": str(e),
                    },
                    "duration_ms": duration,
                }
            )

            logger = RequestContextAdapter(self.logger, extra=context)
            logger.error(
                f"Error processing {request.method} {request.url.path}: {str(e)}"
            )
            raise
