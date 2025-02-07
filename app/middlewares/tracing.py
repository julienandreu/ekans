"""Tracing middleware for request tracking and distributed tracing."""

import time
import uuid
from contextvars import ContextVar
from typing import Awaitable, Callable, Optional

from fastapi import Request, Response
from opentelemetry import trace
from opentelemetry.trace import Span, Status, StatusCode
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Context variable to store the request ID
request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="")
# Context variable to store the correlation ID
correlation_id_ctx_var: ContextVar[Optional[str]] = ContextVar(
    "correlation_id", default=None
)
# Context variable to store the current span
current_span_ctx_var: ContextVar[Optional[Span]] = ContextVar(
    "current_span", default=None
)


class TracingMiddleware(BaseHTTPMiddleware):
    """Middleware for request tracing and span management.

    Args:
        app: ASGI app
        tracer_name: Tracer name
    """

    def __init__(
        self,
        app: ASGIApp,
        tracer_name: str = "ekans.request",
    ) -> None:
        """Initialize the tracing middleware.

        Args:
            app: ASGI app
            tracer_name: Tracer name
        """
        super().__init__(app)
        self.tracer = trace.get_tracer(tracer_name)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Dispatch the request.

        Args:
            request: Request
            call_next: Callable[[Request], Awaitable[Response]]
        """
        request_id = str(uuid.uuid4())
        request_id_ctx_var.set(request_id)

        correlation_id = request.headers.get("X-Correlation-ID")
        correlation_id_ctx_var.set(correlation_id)

        start_time = time.time()

        with self.tracer.start_as_current_span(
            f"{request.method} {request.url.path}",
            kind=trace.SpanKind.SERVER,
        ) as span:
            current_span_ctx_var.set(span)

            # Add basic span attributes
            span_attributes = {
                "http.method": request.method,
                "http.url": str(request.url),
                "http.request_id": request_id,
                "http.route": request.url.path,
            }
            if correlation_id:
                span_attributes["http.correlation_id"] = correlation_id
            span.set_attributes(span_attributes)

            try:
                response = await call_next(request)

                # Add response attributes to span
                span.set_attributes(
                    {
                        "http.status_code": response.status_code,
                        "http.duration": time.time() - start_time,
                    }
                )

                if 200 <= response.status_code < 400:
                    span.set_status(Status(StatusCode.OK))
                else:
                    span.set_status(Status(StatusCode.ERROR))

                # Add request ID and correlation ID to response headers
                response.headers["X-Request-ID"] = request_id
                if correlation_id:
                    response.headers["X-Correlation-ID"] = correlation_id
                return response

            except Exception as e:
                span.set_status(Status(StatusCode.ERROR))
                span.record_exception(e)
                raise


def get_request_id() -> str:
    """Get the current request ID.

    Returns:
        str: Request ID
    """
    return request_id_ctx_var.get()


def get_correlation_id() -> Optional[str]:
    """Get the current correlation ID.

    Returns:
        str: Correlation ID
    """
    return correlation_id_ctx_var.get()


def get_current_span() -> Optional[Span]:
    """Get the current tracing span.

    Returns:
        Optional[Span]: Current span
    """
    return current_span_ctx_var.get()
