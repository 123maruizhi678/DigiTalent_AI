"""FastAPI application assembly and lifecycle entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Reserve startup and shutdown boundaries without external resources."""
    # Future resources must be initialized here and released in finally.
    try:
        yield
    finally:
        pass


settings = get_settings()
app = FastAPI(
    title=settings.APP_NAME, debug=settings.DEBUG, version="0.1.0", lifespan=lifespan
)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
