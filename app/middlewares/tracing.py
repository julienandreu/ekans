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
# Context variable to store the current span
current_span_ctx_var: ContextVar[Optional[Span]] = ContextVar(
    "current_span", default=None
)


class TracingMiddleware(BaseHTTPMiddleware):
    """Middleware for request tracing and span management."""

    def __init__(
        self,
        app: ASGIApp,
        tracer_name: str = "ekans.request",
    ) -> None:
        super().__init__(app)
        self.tracer = trace.get_tracer(tracer_name)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = str(uuid.uuid4())
        request_id_ctx_var.set(request_id)

        start_time = time.time()

        with self.tracer.start_as_current_span(
            f"{request.method} {request.url.path}",
            kind=trace.SpanKind.SERVER,
        ) as span:
            current_span_ctx_var.set(span)

            # Add basic span attributes
            span.set_attributes(
                {
                    "http.method": request.method,
                    "http.url": str(request.url),
                    "http.request_id": request_id,
                    "http.route": request.url.path,
                }
            )

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

                # Add request ID to response headers
                response.headers["X-Request-ID"] = request_id
                return response

            except Exception as e:
                span.set_status(Status(StatusCode.ERROR))
                span.record_exception(e)
                raise


def get_request_id() -> str:
    """Get the current request ID."""
    return request_id_ctx_var.get()


def get_current_span() -> Optional[Span]:
    """Get the current tracing span."""
    return current_span_ctx_var.get()
