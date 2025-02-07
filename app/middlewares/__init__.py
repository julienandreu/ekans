"""HTTP middleware implementations."""

from app.middlewares.stats import HttpStatsMiddleware
from app.middlewares.tracing import TracingMiddleware

available_middlewares = [
    TracingMiddleware,
    HttpStatsMiddleware,
]
