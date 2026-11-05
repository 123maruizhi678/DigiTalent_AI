"""R09 可复用契约；不注册认证路由，不代替持久化会话或 JWT 验证。"""

from typing import Literal

from fastapi import HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field, SecretStr


class LoginRequest(BaseModel):
    """账号密码仅用于身份验证，禁止输出到日志。"""

    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    account: str = Field(min_length=1, max_length=254, description="登录账号")
    password: SecretStr = Field(min_length=1, max_length=1024, description="登录密码，禁止记录")


class CurrentUser(BaseModel):
    """当前用户公开字段白名单。"""

    model_config = ConfigDict(extra="forbid")
    user_id: str = Field(description="用户标识")
    name: str = Field(description="显示名称")
    roles: list[str] = Field(description="角色标识列表")
    permissions: list[str] = Field(description="权限标识列表")


class TokenData(BaseModel):
    """登录和刷新共用返回值；严禁包含 Refresh Token。"""

    model_config = ConfigDict(extra="forbid")
    access_token: str = Field(min_length=1, repr=False, description="短期访问令牌")
    token_type: Literal["Bearer"] = Field(default="Bearer", description="访问令牌类型")
    expires_in: int = Field(default=900, gt=0, le=900, description="访问令牌剩余秒数，最多900秒")
    user: CurrentUser = Field(description="当前用户公开信息")


def require_csrf(request: Request, allowed_origins: frozenset[str]) -> None:
    """写认证请求必须有精确白名单 Origin 和自定义头；缺失 Origin 也拒绝。"""
    origin = request.headers.get("origin")
    if (
        not origin
        or origin == "null"
        or origin not in allowed_origins
        or request.headers.get("x-csrf-protection") != "1"
    ):
        raise HTTPException(status_code=403)


def refresh_cookie(
    response: Response, token: str, *, production: bool, clear: bool = False, max_age: int = 604800
):
    """同站部署使用 Lax、host-only Cookie；生产强制 Secure；删除匹配设置属性。"""
    options = dict(
        key="dt_refresh",
        path="/api/v1/auth",
        httponly=True,
        secure=production,
        samesite="lax",
    )
    if clear:
        response.delete_cookie(**options)
    else:
        if not 0 < max_age <= 604800:
            raise ValueError("Cookie有效期必须为1至604800秒")
        response.set_cookie(value=token, max_age=max_age, **options)
    response.headers["Cache-Control"] = "no-store"
