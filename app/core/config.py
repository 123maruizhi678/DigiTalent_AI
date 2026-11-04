"""统一读取并校验后端配置，不初始化外部服务。"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings.exceptions import SettingsError

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """M0 应用配置；字段均有默认值，外部服务凭据留待对应任务定义。"""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        hide_input_in_errors=True,
        frozen=True,
    )

    # 应用基础配置：均非敏感；允许省略，省略时使用默认值。
    APP_NAME: str = Field(
        default="DigiTalent AI",
        min_length=1,
        repr=False,
        description="应用名称：用于 FastAPI 标题；字符串，去除两端空白后不能为空；默认 DigiTalent AI；非必填、非敏感。",
    )
    APP_ENV: Literal["development", "test", "production"] = Field(
        default="development",
        repr=False,
        description="运行环境：字符串，仅允许 development、test、production；默认 development；非必填、非敏感。",
    )
    DEBUG: bool = Field(
        default=False,
        repr=False,
        description="调试模式：控制 FastAPI 调试开关；布尔值，支持 true/false、1/0、yes/no、on/off；默认 false；非必填、非敏感。",
    )
    API_V1_PREFIX: str = Field(
        default="/api/v1",
        pattern=r"^/[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*$",
        repr=False,
        description="API 版本前缀：挂载总路由；字符串，以 / 开头的非空路径段，允许字母数字下划线连字符，不允许尾斜杠；默认 /api/v1；非必填、非敏感。",
    )
    HOST: str = Field(
        default="127.0.0.1",
        min_length=1,
        repr=False,
        description="监听地址：供 python -m app.main 启动使用；非空字符串，应为有效主机名或 IP；默认 127.0.0.1；非必填、非敏感。",
    )
    PORT: int = Field(
        default=8080,
        ge=1,
        le=65535,
        repr=False,
        description="监听端口：供 python -m app.main 启动使用；整数，范围 1～65535；默认 8080；非必填、非敏感。",
    )

    # 日志配置：本任务仅校验配置，不初始化 BASE-003 日志设施。
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        repr=False,
        description="日志级别：字符串，允许 DEBUG、INFO、WARNING、ERROR、CRITICAL，输入大小写不敏感；默认 INFO；非必填、非敏感。",
    )
    LOG_OUTPUT: Literal["console"] = Field(
        default="console",
        repr=False,
        description="日志输出方式：字符串，M0 只允许 console，不写日志目录；默认 console；非必填、非敏感。",
    )

    # 后续扩展分类：MySQL、Milvus、Ollama、MinerU、文件存储、模型服务、任务调度。
    # 首次实现时再定义字段；凭据应使用 SecretStr、repr=False 和中文说明，禁止明文输出。

    @field_validator("APP_NAME", "HOST", mode="before")
    @classmethod
    def strip_required_text(cls, value: object) -> object:
        """字符串去除两端空白，非空约束由字段统一校验。"""
        return value.strip() if isinstance(value, str) else value

    @field_validator("LOG_LEVEL", mode="before")
    @classmethod
    def normalize_log_level(cls, value: object) -> object:
        """日志级别统一为大写，再由枚举约束校验，错误中不拼接输入值。"""
        return value.upper() if isinstance(value, str) else value


class ConfigurationError(ValueError):
    """仅包含配置项名称的安全启动错误，不携带原始配置输入。"""


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """集中创建不可变配置单例；进程变量覆盖 .env，.env 覆盖默认值。"""
    try:
        return Settings()
    except ValidationError as error:
        fields = sorted(
            {
                str(item["loc"][0])
                for item in error.errors(include_input=False, include_context=False)
            }
        )
        raise ConfigurationError("配置校验失败，请检查配置项：" + ", ".join(fields)) from None
    except SettingsError:
        raise ConfigurationError("配置来源读取失败，请检查环境变量或 .env 文件格式") from None
