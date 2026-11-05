"""Process health endpoint; external dependencies are not checked."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Report that the application can serve HTTP requests."""
    return {"status": "ok", "service": "digitalent-ai"}


@router.get("/health/db")
def database_health(request: Request) -> JSONResponse:
    """数据库就绪检查在线程池执行；不改变进程存活接口。"""
    reason = request.app.state.database.check()
    return JSONResponse(
        {"status": "unavailable" if reason else "ok", "database": "mysql", "reason": reason},
        status_code=503 if reason else 200,
    )
