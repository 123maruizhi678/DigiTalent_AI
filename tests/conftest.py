"""收集应用模块之前隔离真实环境和 .env，测试只使用合成配置。"""

import importlib
import os
from functools import partial

import pytest

from app.core import config
from app.core.config import Settings, get_settings

# 配置测试仍可显式传入临时 _env_file；不读取项目真实配置文件。
_original_env_file = Settings.model_config.get("env_file")
_saved_environment = {
    key: value for key, value in os.environ.items() if key.upper() in Settings.model_fields
}
for _key in _saved_environment:
    del os.environ[_key]
Settings.model_config["env_file"] = None
get_settings.cache_clear()
try:
    importlib.import_module("app.main")
finally:
    Settings.model_config["env_file"] = _original_env_file


@pytest.fixture(autouse=True)
def isolated_application_settings(monkeypatch):
    """每个用例禁用真实 dotenv；保留 Settings 类定义供路径契约测试。"""
    monkeypatch.setattr(config, "Settings", partial(Settings, _env_file=None))
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def pytest_unconfigure(config):
    """测试会话结束恢复宿主环境和配置定义，避免污染嵌入式调用。"""
    Settings.model_config["env_file"] = _original_env_file
    os.environ.update(_saved_environment)
    get_settings.cache_clear()
