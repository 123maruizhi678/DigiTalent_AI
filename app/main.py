"""FastAPI application assembly and lifecycle entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.concurrency import run_in_threadpool

from app.api.router import api_router
from app.core.config import get_settings
from app.core.database import Database
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import RequestTracingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """集中管理数据库资源；网络不可用不影响应用存活。"""
    setup_logging()
    database = await run_in_threadpool(Database, get_settings())
    app.state.database = database
    try:
        yield
    finally:
        await run_in_threadpool(database.close)


settings = get_settings()
app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, version="0.1.0", lifespan=lifespan)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
register_exception_handlers(app)
app.add_middleware(RequestTracingMiddleware)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
