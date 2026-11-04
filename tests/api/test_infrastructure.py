"""日志与请求追踪回归；只使用临时合成数据。"""

import asyncio
import io
import json
import logging
from functools import partial

import httpx
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.core import config
from app.core.config import Settings
from app.core.exceptions import (
    BusinessError,
    ParameterError,
    PermissionError,
    SystemError,
    register_exception_handlers,
)
from app.core.logging import request_id_context, setup_logging
from app.core.middleware import RequestTracingMiddleware


@pytest.fixture
def log_output(monkeypatch):
    for name in Settings.model_fields:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(config, "Settings", partial(Settings, _env_file=None))
    config.get_settings.cache_clear()
    root = logging.getLogger()
    handlers, level = root.handlers[:], root.level
    setup_logging()
    handler = next(h for h in root.handlers if getattr(h, "_digitalent", False))
    stream = io.StringIO()
    previous = handler.stream
    handler.setStream(stream)
    yield stream
    handler.setStream(previous)
    root.handlers[:] = handlers
    root.setLevel(level)
    config.get_settings.cache_clear()


@pytest.fixture
def application():
    app = FastAPI(debug=True)
    register_exception_handlers(app)
    app.add_middleware(RequestTracingMiddleware)

    @app.get("/case/{kind}")
    async def case(kind: str, number: int = 1):
        await asyncio.sleep(0)
        if kind == "business":
            raise BusinessError("资源暂不可用", ["请稍后重试"])
        if kind == "parameter":
            raise ParameterError()
        if kind == "permission":
            raise PermissionError()
        if kind == "system":
            raise SystemError()
        if kind == "http":
            raise HTTPException(
                401, "password=fake-private", headers={"WWW-Authenticate": "Bearer"}
            )
        if kind == "unknown":
            raise RuntimeError("password=fake-private /private/database.sql")
        return {"id": request_id_context.get()}

    return app


def test_logging_configuration_idempotence(log_output, monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    config.get_settings.cache_clear()
    setup_logging()
    setup_logging()
    root = logging.getLogger()
    assert root.level == logging.WARNING
    assert sum(bool(getattr(h, "_digitalent", False)) for h in root.handlers) == 1
    logging.getLogger("app.test").info("invisible")
    logging.getLogger("app.test").warning("visible")
    rows = [json.loads(line) for line in log_output.getvalue().splitlines()]
    assert len(rows) == 1
    assert {"time", "level", "logger", "message", "request_id"} <= rows[0].keys()


def test_sensitive_log_fields_are_omitted(log_output):
    logging.getLogger("app.test").info(
        "password=fake-private token=fake-token user@example.com",
        extra={"resume": "private-resume", "cookie": "private-cookie"},
    )
    output = log_output.getvalue()
    assert all(
        secret not in output
        for secret in [
            "fake-private",
            "fake-token",
            "user@example.com",
            "private-resume",
            "private-cookie",
        ]
    )


@pytest.mark.parametrize("external", [None, "trusted_123-ABC", "bad id", "x" * 65, ""])
def test_request_ids(application, log_output, external):
    headers = {} if external is None else {"X-Request-ID": external}
    with TestClient(application) as client:
        response = client.get("/case/ok?token=fake-query", headers=headers)
    rid = response.headers["x-request-id"]
    assert response.json()["id"] == rid
    assert rid == external if external == "trusted_123-ABC" else rid.startswith("req_")
    rows = [json.loads(line) for line in log_output.getvalue().splitlines()]
    request_log = next(row for row in rows if row["message"] == "请求处理完成")
    assert request_log["request_id"] == rid
    assert request_log["path"] == "/case/{kind}"
    assert request_log["status_code"] == 200
    assert request_log["duration_ms"] >= 0
    assert request_id_context.get() is None


@pytest.mark.parametrize(
    "kind,status,code",
    [
        ("business", 400, "BUSINESS_ERROR"),
        ("parameter", 422, "PARAMETER_ERROR"),
        ("permission", 403, "PERMISSION_ERROR"),
        ("system", 500, "SYSTEM_ERROR"),
        ("http", 401, "AUTHENTICATION_ERROR"),
        ("unknown", 500, "SYSTEM_ERROR"),
        ("ok?number=fake-private", 422, "PARAMETER_ERROR"),
    ],
)
def test_error_contract(application, log_output, kind, status, code):
    with TestClient(application, raise_server_exceptions=False) as client:
        response = client.get("/case/" + kind)
    body = response.json()
    assert response.status_code == status
    assert set(body) == {"code", "message", "data", "request_id"}
    assert body["code"] == code
    assert isinstance(body["data"]["errors"], list)
    assert body["request_id"] == response.headers["x-request-id"]
    assert "fake-private" not in response.text + log_output.getvalue()
    assert "/private/" not in response.text
    assert request_id_context.get() is None
    if kind == "business":
        assert body["message"] == "资源暂不可用"
    if kind == "http":
        assert response.headers["www-authenticate"] == "Bearer"
    if kind == "unknown":
        assert "frames" in log_output.getvalue()
        assert "Traceback" not in response.text


def test_concurrent_context_isolation(application, log_output):
    async def run():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=application), base_url="http://test"
        ) as client:
            responses = await asyncio.gather(
                *[client.get("/case/ok", headers={"X-Request-ID": f"id_{i}"}) for i in range(12)]
            )
        assert [r.json()["id"] for r in responses] == [f"id_{i}" for i in range(12)]
        assert request_id_context.get() is None

    asyncio.run(run())


def test_duplicate_headers_replaced(application):
    with TestClient(application) as client:
        response = client.get("/case/ok", headers=[("X-Request-ID", "a"), ("X-Request-ID", "b")])
    assert response.headers["x-request-id"].startswith("req_")


def test_client_query_not_logged(application, log_output):
    with TestClient(application) as client:
        client.get("/case/ok?access_token=private-query-value")
    assert "private-query-value" not in log_output.getvalue()


def test_cancellation_restores_parent_context():
    async def run():
        async def cancelled(scope, receive, send):
            raise asyncio.CancelledError()

        middleware = RequestTracingMiddleware(cancelled)
        token = request_id_context.set("parent")
        try:
            with pytest.raises(asyncio.CancelledError):
                await middleware({"type": "http", "method": "GET", "headers": []}, None, None)
            assert request_id_context.get() == "parent"
        finally:
            request_id_context.reset(token)

    asyncio.run(run())
