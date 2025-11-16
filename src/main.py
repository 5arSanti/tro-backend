from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.app.core.config import settings
from src.app.core.middleware import MaxRequestSizeMiddleware
from src.app.file_classification.file_classification_controller import (
    router as file_classification_router,
)
from src.app.health.health_controller import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield


def create_app() -> FastAPI:
    app: FastAPI = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="TRO Backend Project with FastAPI",
        debug=settings.debug,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add middleware to limit request body size to 2GB
    app.add_middleware(MaxRequestSizeMiddleware)

    app.include_router(health_router, prefix=settings.api_v1_prefix)

    return app


app: FastAPI = create_app()
