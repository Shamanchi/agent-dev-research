"""Точка входа FastAPI."""

from fastapi import FastAPI

from app.api.brief import router as brief_router
from app.api.health import router as health_router
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="agent-dev-research", version="0.1.0")
    app.include_router(health_router, prefix="/api/v1", tags=["health"])
    app.include_router(brief_router, prefix="/api/v1", tags=["brief"])
    return app


app = create_app()
