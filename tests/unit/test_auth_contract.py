"""R09 契约组件验证；不冒充尚不存在的 IAM API 集成测试。"""

import pytest
from fastapi import HTTPException, Response
from pydantic import ValidationError
from starlette.requests import Request

from app.common.auth_contract import LoginRequest, TokenData, refresh_cookie, require_csrf


@pytest.mark.parametrize("production", [False, True])
@pytest.mark.parametrize("clear", [False, True])
def test_cookie(production, clear):
    response = Response()
    refresh_cookie(response, "synthetic-refresh", production=production, clear=clear)
    cookie = response.headers["set-cookie"]
    assert "HttpOnly" in cookie and "SameSite=lax" in cookie
    assert "Path=/api/v1/auth" in cookie and "Domain=" not in cookie
    assert ("Secure" in cookie) == production
    assert ("Max-Age=0" if clear else "Max-Age=604800") in cookie
    assert response.headers["cache-control"] == "no-store"


@pytest.mark.parametrize(
    "origin,header,allowed",
    [
        ("https://app.example", "1", True),
        ("https://evil.example", "1", False),
        ("https://app.example.evil", "1", False),
        ("null", "1", False),
        ("", "1", False),
        ("https://app.example", "", False),
    ],
)
def test_csrf(origin, header, allowed):
    request = Request(
        {
            "type": "http",
            "headers": [
                (b"origin", origin.encode()),
                (b"x-csrf-protection", header.encode()),
            ],
        }
    )
    if allowed:
        require_csrf(request, frozenset({"https://app.example"}))
    else:
        with pytest.raises(HTTPException) as error:
            require_csrf(request, frozenset({"https://app.example"}))
        assert error.value.status_code == 403


def test_response_whitelist():
    payload = dict(
        access_token="synthetic-access",
        user=dict(user_id="u1", name="测试", roles=[], permissions=[]),
    )
    assert "refresh_token" not in TokenData(**payload).model_dump()
    with pytest.raises(ValidationError):
        TokenData(**payload, refresh_token="synthetic-refresh")
    with pytest.raises(ValidationError):
        TokenData(**{**payload, "user": {**payload["user"], "password": "secret"}})


def test_password_not_in_repr():
    assert "synthetic-password" not in repr(
        LoginRequest(account="test", password="synthetic-password")
    )


@pytest.mark.parametrize("age", [0, -1, 604801])
def test_cookie_rejects_invalid_age(age):
    with pytest.raises(ValueError):
        refresh_cookie(Response(), "synthetic", production=True, max_age=age)


def test_cookie_remaining_lifetime():
    response = Response()
    refresh_cookie(response, "synthetic", production=True, max_age=123)
    assert "Max-Age=123" in response.headers["set-cookie"]
