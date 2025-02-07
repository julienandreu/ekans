"""Ekans API: A simple FastAPI application."""

from fastapi import FastAPI

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

# Add middlewares
app.add_middleware(TracingMiddleware)
app.add_middleware(HttpStatsMiddleware)
app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, server_header=False)
