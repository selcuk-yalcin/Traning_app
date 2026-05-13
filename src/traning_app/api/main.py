"""ASGI application factory."""

from fastapi import FastAPI

from traning_app.api.routes import health, presentations


def create_app() -> FastAPI:
    app = FastAPI(title="Traning_app Engine", version="0.1.0")
    app.include_router(health.router, tags=["health"])
    app.include_router(presentations.router)
    return app


app = create_app()
