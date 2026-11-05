"""按需组合的公共字段；默认值及更新时间均在 SQLAlchemy 执行写入时生成。

直接执行原始 SQL 的调用方须显式提供 UUID、UTC 时间；不依赖数据库会话时区。
created_at 无 onupdate，普通更新保留原值，但不禁止显式修正该字段。
"""

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, Uuid
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import TypeDecorator


def utc_now() -> datetime:
    """统一生成带 UTC 时区、微秒精度的当前时间。"""
    return datetime.now(UTC)


class UTCDateTime(TypeDecorator):
    """Python 使用 aware UTC；数据库保存无时区 UTC，MySQL 精度为六位小数。

    拒绝无时区输入，避免将本地时间误作 UTC；读取时恢复 UTC 时区。
    """

    impl = DateTime
    cache_ok = True

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(DATETIME(fsp=6) if dialect.name == "mysql" else DateTime())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("时间必须包含时区")
        return value.astimezone(UTC).replace(tzinfo=None)

    def process_result_value(self, value, dialect):
        return value.replace(tzinfo=UTC) if value is not None else None


class RecordStatus(StrEnum):
    """公共记录可用性；禁止用于账号、任务执行或审批流程状态。"""

    ACTIVE = "active"
    INACTIVE = "inactive"


class RecordStatusType(TypeDecorator):
    """Python 只接受 RecordStatus；数据库 VARCHAR(8) 加 CHECK 约束。"""

    impl = Enum
    cache_ok = True

    def __init__(self):
        super().__init__(
            RecordStatus,
            values_callable=lambda enum: [item.value for item in enum],
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            name="record_status",
        )

    def process_bind_param(self, value, dialect):
        if value is not None and not isinstance(value, RecordStatus):
            raise ValueError("公共记录状态必须使用 RecordStatus，不能混用业务状态")
        return value


class UUIDPrimaryKeyMixin:
    """默认主键规范：写入时生成 UUID4；Python UUID，数据库 CHAR(32) 小写十六进制。

    外键使用相同 Uuid(as_uuid=True, native_uuid=False) 类型；API 使用 Pydantic
    UUID 字段或 str(uuid) 序列化为带连字符的标准字符串。
    """

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True, native_uuid=False),
        primary_key=True,
        default=uuid4,
        comment="统一 UUID4 主键，CHAR(32) 存储",
    )


class TimestampMixin:
    """创建及更新时间；统一 SQLAlchemy 客户端默认值和 onupdate。"""

    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=utc_now, nullable=False, comment="创建时间，UTC 微秒精度"
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime(),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
        comment="最近更新时间，UTC 微秒精度",
    )


class RecordStatusMixin:
    """按需继承：status 默认 active，仅允许 active/inactive，不表达业务流程。"""

    status: Mapped[RecordStatus] = mapped_column(
        RecordStatusType(),
        default=RecordStatus.ACTIVE,
        server_default="active",
        nullable=False,
        comment="公共记录状态：active 可用，inactive 停用",
    )
