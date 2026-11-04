"""通用安全异常及统一响应，不包含具体业务或认证实现。"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.core.logging import request_id_context, safe_text

logger = logging.getLogger(__name__)


class ApplicationError(Exception):
    """message 和 errors 只能使用开发者确认可公开的信息，禁止传入原始异常。"""

    code = "SYSTEM_ERROR"
    status_code = 500
    default_message = "系统处理失败"

    def __init__(self, message: str | None = None, errors: list[str] | None = None):
        self.message = safe_text(message or self.default_message)
        self.errors = [safe_text(item) for item in (errors or [])]
        super().__init__(self.message)


class ParameterError(ApplicationError):
    code = "PARAMETER_ERROR"
    status_code = 422
    default_message = "请求参数错误"


class BusinessError(ApplicationError):
    code = "BUSINESS_ERROR"
    status_code = 400
    default_message = "业务处理失败"


class PermissionError(ApplicationError):
    code = "PERMISSION_ERROR"
    status_code = 403
    default_message = "无权执行此操作"


class SystemError(ApplicationError):
    """系统异常禁止覆盖客户端通用消息。"""

    def __init__(self):
        super().__init__()


def error_response(
    code: str, message: str, status: int, errors: list | None = None, headers: dict | None = None
) -> JSONResponse:
    request_id = request_id_context.get()
    return JSONResponse(
        {
            "code": code,
            "message": message,
            "data": {"errors": errors or []},
            "request_id": request_id,
        },
        status_code=status,
        headers={**(headers or {}), "X-Request-ID": request_id or ""},
    )


async def application_error_handler(request: Request, exc: ApplicationError):
    return error_response(exc.code, exc.message, exc.status_code, exc.errors)


async def http_error_handler(request: Request, exc: HTTPException):
    code = {401: "AUTHENTICATION_ERROR", 403: "PERMISSION_ERROR"}.get(
        exc.status_code, "SYSTEM_ERROR" if exc.status_code >= 500 else "PARAMETER_ERROR"
    )
    # HTTPException.detail 可能是原始数据库错误或用户输入，采用固定安全文案。
    return error_response(
        code,
        "系统处理失败" if exc.status_code >= 500 else "请求无法处理",
        exc.status_code,
        headers=exc.headers,
    )


async def validation_error_handler(request: Request, exc: RequestValidationError):
    # 不回传 input、ctx、原始 msg 或可能由用户控制的字典键。
    errors = [
        {
            "location": str(item["loc"][0]) if item.get("loc") else "request",
            "message": "参数类型、格式或取值不符合要求",
        }
        for item in exc.errors()
    ]
    return error_response("PARAMETER_ERROR", "请求参数错误", 422, errors)


async def unexpected_error_handler(request: Request, exc: Exception):
    logger.error("未预期的系统异常", exc_info=(type(exc), exc, exc.__traceback__))
    return error_response("SYSTEM_ERROR", "系统处理失败", 500)


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApplicationError, application_error_handler)
    app.add_exception_handler(HTTPException, http_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, unexpected_error_handler)
