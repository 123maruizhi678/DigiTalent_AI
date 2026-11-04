"""统一控制台 JSON 日志；禁止调用方传入原始业务数据或凭据。"""

from contextvars import ContextVar
from datetime import datetime, timezone
import json
import logging
import re
import traceback

from app.core.config import get_settings

request_id_context: ContextVar[str | None] = ContextVar("request_id", default=None)


def safe_text(value: str) -> str:
    """防御性遮盖常见凭据、连接串、联系方式；不替代调用方的数据最小化。"""
    value = re.sub(r"(?i)\b(?:password|passwd|access_token|refresh_token|token|cookie|api[_-]?key|authorization|密码)\b\s*[:=]\s*(?:Bearer\s+)?[^\s,;]+", "[REDACTED]", value)
    value = re.sub(r"\b[a-zA-Z][a-zA-Z0-9+.-]*://[^\s]+", "[REDACTED_URL]", value)
    value = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|\b\d{11,18}[Xx]?\b", "[REDACTED]", value)
    return value


class JsonFormatter(logging.Formatter):
    """仅输出明确允许的字段，不序列化任意 extra、异常消息或局部变量。"""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "time": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": safe_text(record.getMessage()),
            "request_id": request_id_context.get(),
        }
        for key in ("method", "path", "status_code", "duration_ms"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        if record.exc_info and record.exc_info[2]:
            # 只保留文件名、函数名及行号；不包含绝对路径、源码、异常值和 locals。
            payload["frames"] = [
                {"file": frame.filename.replace("\\", "/").rsplit("/", 1)[-1],
                 "function": frame.name, "line": frame.lineno}
                for frame in traceback.extract_tb(record.exc_info[2])
            ]
        return json.dumps(payload, ensure_ascii=False)


def setup_logging() -> None:
    """消费统一配置；接管运行日志及 Uvicorn 输出，重复调用不增加 handler。"""
    settings = get_settings()
    if settings.LOG_OUTPUT != "console":
        raise ValueError("日志输出仅支持控制台")
    root = logging.getLogger()
    owned = next((h for h in root.handlers if getattr(h, "_digitalent", False)), None)
    if owned is None:
        owned = logging.StreamHandler()
        owned._digitalent = True
        root.addHandler(owned)
    owned.setFormatter(JsonFormatter())
    root.setLevel(settings.LOG_LEVEL)
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(name)
        logger.handlers.clear()
        logger.propagate = True
    # 统一请求日志已包含必要字段，关闭可能携带查询串的第三方 access 日志。
    logging.getLogger("uvicorn.access").disabled = True
    # HTTPX 默认 INFO 请求日志会输出完整查询串；运行日志不采集此类信息。
    for name in ("httpx", "httpcore"):
        logging.getLogger(name).setLevel(logging.WARNING)
