"""验证已注册路由和 Cookie 路径，不冒充未实现的业务 API。"""

import httpx
import pytest
from fastapi import Response

from app.common.auth_contract import refresh_cookie
from app.main import app


def test_registered_api_paths():
    assert set(app.openapi()["paths"]) == {"/api/v1/health", "/api/v1/health/db"}


@pytest.mark.parametrize("production", [False, True])
def test_cookie_scope_and_deletion(production):
    response = Response()
    refresh_cookie(response, "synthetic", production=production)
    with httpx.Client(base_url="https://example.test") as client:
        login = client.build_request("POST", "/api/v1/auth/login")
        client.cookies.extract_cookies(httpx.Response(200, headers=response.headers, request=login))
        for action in ["login", "refresh", "logout", "me"]:
            request = client.build_request("POST", f"/api/v1/auth/{action}")
            assert request.headers["cookie"] == "dt_refresh=synthetic"
        for path in ["/api/v1/files", "/api/v1/authentication", "/api/auth/refresh"]:
            assert "cookie" not in client.build_request("GET", path).headers
        cleared = Response()
        refresh_cookie(cleared, "", production=production, clear=True)
        logout = client.build_request("POST", "/api/v1/auth/logout")
        client.cookies.extract_cookies(httpx.Response(200, headers=cleared.headers, request=logout))
        assert "cookie" not in client.build_request("POST", "/api/v1/auth/refresh").headers
