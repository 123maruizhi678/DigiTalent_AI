"""配置来源、校验和安全错误回归测试，不读取真实 .env。"""

import importlib
from functools import partial

import pytest
from fastapi.testclient import TestClient
from pydantic import Field, ValidationError

from app.core import config
from app.core.config import ConfigurationError, Settings, get_settings


@pytest.fixture(autouse=True)
def isolated_settings(monkeypatch):
    for name in Settings.model_fields:
        monkeypatch.delenv(name, raising=False)
        monkeypatch.delenv(name.lower(), raising=False)
    monkeypatch.setattr(config, "Settings", partial(Settings, _env_file=None))
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_defaults():
    settings = get_settings()
    assert settings.model_dump() == {
        "APP_NAME": "DigiTalent AI",
        "APP_ENV": "development",
        "DEBUG": False,
        "API_V1_PREFIX": "/api/v1",
        "HOST": "127.0.0.1",
        "PORT": 8080,
        "LOG_LEVEL": "INFO",
        "LOG_OUTPUT": "console",
    }


def test_environment_overrides(monkeypatch):
    for name, value in {
        "APP_NAME": "环境测试",
        "APP_ENV": "test",
        "DEBUG": "true",
        "API_V1_PREFIX": "/api/test",
        "HOST": "0.0.0.0",
        "PORT": "8123",
        "LOG_LEVEL": "warning",
    }.items():
        monkeypatch.setenv(name, value)
    settings = get_settings()
    assert (settings.APP_NAME, settings.APP_ENV, settings.DEBUG) == ("环境测试", "test", True)
    assert (settings.API_V1_PREFIX, settings.HOST, settings.PORT, settings.LOG_LEVEL) == (
        "/api/test",
        "0.0.0.0",
        8123,
        "WARNING",
    )


def test_dotenv_priority_and_unknown_secret(tmp_path, monkeypatch):
    dotenv = tmp_path / ".env"
    dotenv.write_text(
        "APP_NAME=文件配置\nPORT=8124\nMYSQL_PASSWORD=fake-secret\n", encoding="utf-8"
    )
    monkeypatch.setenv("PORT", "8125")
    settings = Settings(_env_file=dotenv)
    assert settings.APP_NAME == "文件配置"
    assert settings.PORT == 8125
    assert "fake-secret" not in repr(settings)
    assert "MYSQL_PASSWORD" not in settings.model_dump()


@pytest.mark.parametrize("value", ["1", "8080", "65535"])
def test_valid_ports(monkeypatch, value):
    monkeypatch.setenv("PORT", value)
    assert get_settings().PORT == int(value)


@pytest.mark.parametrize("value", ["0", "65536", "-1", "bad", "8.5"])
def test_invalid_ports(monkeypatch, value):
    monkeypatch.setenv("PORT", value)
    with pytest.raises(ConfigurationError, match="PORT"):
        get_settings()


@pytest.mark.parametrize(
    "value, expected",
    [("true", True), ("false", False), ("1", True), ("0", False), ("yes", True), ("off", False)],
)
def test_bool_parsing(monkeypatch, value, expected):
    monkeypatch.setenv("DEBUG", value)
    assert get_settings().DEBUG is expected


@pytest.mark.parametrize(
    "field, value",
    [
        ("LOG_LEVEL", "TRACE"),
        ("APP_ENV", "invalid"),
        ("DEBUG", "maybe"),
        ("APP_NAME", " "),
        ("API_V1_PREFIX", "api/v1"),
        ("API_V1_PREFIX", "/api/v1/"),
        ("HOST", ""),
        ("LOG_OUTPUT", "file"),
    ],
)
def test_invalid_fields(monkeypatch, field, value):
    monkeypatch.setenv(field, value)
    with pytest.raises(ConfigurationError, match=field):
        get_settings()


def test_safe_errors_and_repr(monkeypatch):
    fake_secret = "fake-password-token-do-not-log"
    monkeypatch.setenv("PORT", fake_secret)
    with pytest.raises(ConfigurationError) as caught:
        get_settings()
    assert "PORT" in str(caught.value)
    assert fake_secret not in str(caught.value)
    assert fake_secret not in repr(caught.value)
    assert caught.value.__suppress_context__
    with pytest.raises(ValidationError) as direct:
        Settings(_env_file=None)
    assert fake_secret not in str(direct.value)
    assert "private-title" not in repr(
        Settings(_env_file=None, PORT=8080, APP_NAME="private-title")
    )


def test_future_required_field_error():
    class RequiredSettings(Settings):
        APP_NAME: str = Field(description="应用名称：本测试设为必填，用于验证缺失错误。")

    with pytest.raises(ValidationError) as caught:
        RequiredSettings(_env_file=None)
    assert "APP_NAME" in str(caught.value)
    assert "Field required" in str(caught.value)


def test_singleton_and_immutability():
    assert get_settings() is get_settings()
    with pytest.raises(ValidationError):
        get_settings().PORT = 9000


def test_project_env_path_is_independent_of_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert Settings.model_config["env_file"] == config.PROJECT_ROOT / ".env"


def test_example_matches_field_names():
    example = Settings(_env_file=config.PROJECT_ROOT / ".env.example")
    assert example.model_dump() == get_settings().model_dump()
    assert all(
        field.description and any("\u4e00" <= char <= "\u9fff" for char in field.description)
        for field in Settings.model_fields.values()
    )


def test_fastapi_configured_prefix_preserves_health(monkeypatch):
    from app import main

    monkeypatch.setenv("APP_NAME", "配置集成验证")
    monkeypatch.setenv("API_V1_PREFIX", "/api/test")
    monkeypatch.setenv("DEBUG", "true")
    try:
        importlib.reload(main)
        assert main.settings is get_settings()
        assert main.app.title == "配置集成验证"
        assert main.app.debug is True
        with TestClient(main.app) as client:
            assert client.get("/api/test/health").json() == {
                "status": "ok",
                "service": "digitalent-ai",
            }
            assert client.get("/api/v1/health").status_code == 404
    finally:
        for name in ("APP_NAME", "API_V1_PREFIX", "DEBUG"):
            monkeypatch.delenv(name)
        get_settings.cache_clear()
        importlib.reload(main)
