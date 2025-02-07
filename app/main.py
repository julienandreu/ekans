"""Ekans API: A simple FastAPI application."""

from fastapi import FastAPI

from app.middlewares.http_stats import HttpStatsMiddleware
from app.routers import router

app: FastAPI = FastAPI(
    title="Ekans API",
    description="🐍 A simple FastAPI application",
    version="0.1.0",
)

app.add_middleware(HttpStatsMiddleware)
app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
