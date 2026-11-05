"""统一读取并校验后端配置，不初始化外部服务。"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, ValidationError, field_validator
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
    API_V1_PREFIX: Literal["/api/v1"] = Field(
        default="/api/v1",
        repr=False,
        description="API_V1_PREFIX API 版本前缀：挂载总路由；字符串，仅允许 /api/v1；默认 /api/v1；非必填、非敏感，所有环境保持一致。",
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

    # MySQL 配置：允许不配置凭据以保留应用存活检查；连接检查时报告未配置。
    MYSQL_HOST: str = Field(
        default="127.0.0.1",
        min_length=1,
        repr=False,
        description="MYSQL_HOST 主机地址；非空主机名或 IP；类型 str；默认127.0.0.1；非必填、非敏感。",
    )
    MYSQL_PORT: int = Field(
        default=3306,
        ge=1,
        le=65535,
        repr=False,
        description="MYSQL_PORT 端口；整数 1～65535；类型 int；默认3306；非必填、非敏感。",
    )
    MYSQL_USER: str = Field(
        default="",
        repr=False,
        description="MYSQL_USER 用户名；字符串，空值表示未配置；类型 str；默认空字符串；非必填、非敏感。",
    )
    MYSQL_PASSWORD: SecretStr = Field(
        default=SecretStr(""),
        repr=False,
        description="MYSQL_PASSWORD 密码；字符串，可为空，敏感且脱敏；类型 SecretStr；默认空字符串；非必填、敏感。",
    )
    MYSQL_DATABASE: str = Field(
        default="",
        repr=False,
        description="MYSQL_DATABASE 数据库名；字符串，空值表示未配置；类型 str；默认空字符串；非必填、非敏感。",
    )
    MYSQL_POOL_SIZE: int = Field(
        default=5,
        ge=1,
        le=100,
        repr=False,
        description="MYSQL_POOL_SIZE 基础连接数；整数 1～100；类型 int；默认5；非必填、非敏感。",
    )
    MYSQL_MAX_OVERFLOW: int = Field(
        default=10,
        ge=0,
        le=100,
        repr=False,
        description="MYSQL_MAX_OVERFLOW 额外连接数；整数 0～100；类型 int；默认10；非必填、非敏感。",
    )
    MYSQL_POOL_TIMEOUT: int = Field(
        default=30,
        ge=1,
        le=300,
        repr=False,
        description="MYSQL_POOL_TIMEOUT 获取连接等待秒数；整数 1～300；类型 int；默认30；非必填、非敏感。",
    )
    MYSQL_POOL_RECYCLE: int = Field(
        default=1800,
        ge=1,
        le=86400,
        repr=False,
        description="MYSQL_POOL_RECYCLE 连接回收秒数；整数 1～86400；类型 int；默认1800；非必填、非敏感。",
    )
    MYSQL_CONNECT_TIMEOUT: int = Field(
        default=5,
        ge=1,
        le=60,
        repr=False,
        description="MYSQL_CONNECT_TIMEOUT 建立连接超时秒数；整数 1～60；类型 int；默认5；非必填、非敏感。",
    )

    # 后续扩展分类：MySQL、Milvus、Ollama、MinerU、文件存储、模型服务、任务调度。
    # 首次实现时再定义字段；凭据应使用 SecretStr、repr=False 和中文说明，禁止明文输出。

    @field_validator(
        "APP_NAME", "HOST", "MYSQL_HOST", "MYSQL_USER", "MYSQL_DATABASE", mode="before"
    )
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
