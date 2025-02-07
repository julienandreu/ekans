"""Ekans API: A simple FastAPI application."""

from typing import Any, Dict

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.core.tracing import setup_tracing
from app.middlewares.stats import HttpStatsMiddleware
from app.middlewares.tracing import TracingMiddleware
from app.routers import router

# Initialize tracing
setup_tracing(
    service_name="ekans",
    # Configure your tracing endpoint based on your provider:
    # Datadog: "http://localhost:8126"
    # NewRelic: "https://otlp.nr-data.net:4317"
    # Sentry: "http://localhost:4317"
)

app: FastAPI = FastAPI(
    title="Ekans API",
    description="🐍 A simple FastAPI application",
    version="0.1.0",
)


def custom_openapi() -> Dict[str, Any]:
    """Customize the OpenAPI schema.

    Returns:
        Dict[str, Any]: Customized OpenAPI schema
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add global header parameters
    openapi_schema["components"]["parameters"] = {
        "X-Correlation-ID": {
            "name": "X-Correlation-ID",
            "in": "header",
            "description": (
                "Unique identifier for tracing requests " "across multiple services"
            ),
            "schema": {"type": "string", "format": "uuid"},
            "required": False,
        },
    }

    # Add response headers documentation
    openapi_schema["components"]["headers"] = {
        "X-Request-ID": {
            "description": "Unique identifier for the request",
            "schema": {"type": "string", "format": "uuid"},
            "required": True,
        },
        "X-Correlation-ID": {
            "description": "Echo of the request correlation ID if provided",
            "schema": {"type": "string", "format": "uuid"},
            "required": False,
        },
    }

    # Add headers to all responses
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            if "responses" in operation:
                for response in operation["responses"].values():
                    response["headers"] = {
                        "X-Request-ID": {"$ref": "#/components/headers/X-Request-ID"},
                        "X-Correlation-ID": {
                            "$ref": "#/components/headers/X-Correlation-ID"
                        },
                    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore

# Add middlewares
app.add_middleware(TracingMiddleware)
app.add_middleware(HttpStatsMiddleware)
app.include_router(router)

if __name__ == "__main__":
    from uvicorn import run

    run(app, host="0.0.0.0", port=8000, server_header=False)
