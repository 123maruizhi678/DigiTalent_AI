"""纯 ASGI 请求追踪，覆盖异常响应并按 token 恢复上下文。"""

import logging
import re
from time import perf_counter
from uuid import uuid4

from starlette.requests import Request

from app.core.exceptions import unexpected_error_handler
from app.core.logging import request_id_context

logger = logging.getLogger(__name__)
REQUEST_ID_PATTERN = re.compile(r"[A-Za-z0-9_-]{1,64}")


class RequestTracingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        values = [v.decode("latin-1") for k, v in scope["headers"] if k.lower() == b"x-request-id"]
        request_id = (
            values[0]
            if len(values) == 1 and REQUEST_ID_PATTERN.fullmatch(values[0])
            else "req_" + uuid4().hex
        )
        token = request_id_context.set(request_id)
        scope.setdefault("state", {})["request_id"] = request_id
        start, status, started = perf_counter(), 500, False

        async def traced_send(message):
            nonlocal status, started
            if message["type"] == "http.response.start":
                status, started = message["status"], True
                message = dict(message)
                message["headers"] = [
                    (k, v) for k, v in message.get("headers", []) if k.lower() != b"x-request-id"
                ] + [(b"x-request-id", request_id.encode("ascii"))]
            await send(message)

        try:
            try:
                await self.app(scope, receive, traced_send)
            except Exception as exc:
                if started:
                    # 流式响应已经开始后不能重新发送 JSON；保留安全诊断再交给服务器断开连接。
                    await unexpected_error_handler(Request(scope), exc)
                    raise
                response = await unexpected_error_handler(Request(scope), exc)
                await response(scope, receive, traced_send)
        finally:
            try:
                # 使用路由模板防止路径参数包含个人信息；不输出查询串或未知路径。
                route = scope.get("route")
                logger.info(
                    "请求处理完成",
                    extra={
                        "method": scope["method"],
                        "path": getattr(route, "path", "<unmatched>"),
                        "status_code": status,
                        "duration_ms": round((perf_counter() - start) * 1000, 3),
                    },
                )
            finally:
                request_id_context.reset(token)
