"""ASGI application factory."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from traning_app.api.routes import health, presentations


def create_app() -> FastAPI:
    app = FastAPI(title="Traning_app Engine", version="0.1.0")
    origins = [
        o.strip()
        for o in os.environ.get(
            "CORS_ALLOW_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if o.strip()
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins if origins else ["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router, tags=["health"])
    app.include_router(presentations.router)
    return app


app = create_app()
