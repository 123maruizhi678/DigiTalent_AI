"""IAM 三表映射；字段及约束遵循 P6-IAM-001 V1.2。

仅声明结构，不连接数据库。树规则、不可恢复触发器和邀请事务由后续阶段实现。
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CHAR,
    Boolean,
    CheckConstraint,
    Computed,
    ForeignKey,
    Index,
    String,
    Uuid,
    text,
)
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from app.core.model_mixins import (
    RecordStatusMixin,
    TimestampMixin,
    UTCDateTime,
    UUIDPrimaryKeyMixin,
)
from app.core.orm import Base

# 用 UTF-8 十六进制 SQL 字面量表达 ICU 模式，避免反斜线受 SQL 模式影响。
_W = r"\x{0009}-\x{000D}\x{001C}-\x{0020}\x{0085}\x{00A0}\x{1680}\x{2000}-\x{200A}\x{2028}\x{2029}\x{202F}\x{205F}\x{3000}"


def _regexp(column: str, pattern: str) -> str:
    literal = pattern.encode("utf-8").hex()
    return f"REGEXP_LIKE({column}, CONVERT(X'{literal}' USING utf8mb4), 'c')"


def _display(column: str) -> str:
    invalid = _regexp(column, rf"^[{_W}]|[{_W}]$|[\p{{Cc}}\p{{Cf}}]")
    return f"({column} IS NOT NULL AND CHAR_LENGTH({column}) > 0 AND NOT {invalid})"


def _identifier(column: str) -> str:
    return f"({_display(column)} AND NOT {_regexp(column, f'[{_W}]')})"


def _optional_display(column: str) -> str:
    return f"({column} IS NULL OR {_display(column)})"


def _ascii(column: str) -> str:
    return f"({_display(column)} AND NOT {_regexp(column, '[^!-~]')})"


_EMAIL = (
    f"(email IS NULL OR ({_ascii('email')} AND "
    "email = LOWER(email) COLLATE utf8mb4_0900_bin AND "
    "CHAR_LENGTH(email) - CHAR_LENGTH(REPLACE(email, '@', '')) = 1 AND "
    "LEFT(email, 1) <> '@' AND RIGHT(email, 1) <> '@'))"
)
_PHONE = f"(phone IS NULL OR ({_display('phone')} AND {_regexp('phone', '^[+][1-9][0-9]{0,14}$')}))"
_INVITATION = """
((invitation_issued_at IS NULL AND invitation_token_hash IS NULL
  AND invitation_expires_at IS NULL AND invitation_sent_at IS NULL
  AND invitation_accepted_at IS NULL AND invitation_revoked_at IS NULL)
 OR (invitation_issued_at IS NOT NULL AND invitation_expires_at IS NOT NULL
  AND invitation_expires_at > invitation_issued_at
  AND (invitation_sent_at IS NULL OR invitation_sent_at >= invitation_issued_at)
  AND (invitation_accepted_at IS NULL OR
       (invitation_accepted_at >= invitation_issued_at
        AND invitation_accepted_at < invitation_expires_at))
  AND (invitation_revoked_at IS NULL OR invitation_revoked_at >= invitation_issued_at)
  AND (invitation_accepted_at IS NULL OR invitation_revoked_at IS NULL)
  AND ((invitation_accepted_at IS NULL AND invitation_revoked_at IS NULL)
       OR invitation_token_hash IS NULL)
  AND (invitation_accepted_at IS NOT NULL OR invitation_revoked_at IS NOT NULL
       OR is_deleted = 1 OR invitation_token_hash IS NOT NULL)))
""" + (
    " AND (invitation_token_hash IS NULL OR (CHAR_LENGTH(invitation_token_hash) = 64 AND "
    f"NOT {_regexp('invitation_token_hash', '[^0-9a-f]')}))"
)
_TABLE_OPTIONS = {
    "mysql_engine": "InnoDB",
    "mysql_charset": "utf8mb4",
    "mysql_collate": "utf8mb4_0900_bin",
}
_ACTIVE = "CASE WHEN is_deleted=0 THEN 1 ELSE NULL END"


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """账号及当前邀请代次；安全摘要默认延迟加载。"""

    __tablename__ = "sys_user"
    __table_args__ = (
        Index("uq_sys_user_username_active", "username", "active_key", unique=True),
        Index("uq_sys_user_email_active", "email", "active_key", unique=True),
        Index("uq_sys_user_phone_active", "phone", "active_key", unique=True),
        Index("uq_sys_user_invitation_hash", "invitation_token_hash", unique=True),
        Index("ix_sys_user_deleted_status", "is_deleted", "status"),
        CheckConstraint("is_deleted IN (0,1)", name="deleted"),
        CheckConstraint(
            f"{_identifier('username')} AND {_display('real_name')}", name="required_text"
        ),
        CheckConstraint(
            f"{_optional_display('nickname')} AND {_optional_display('display_name')} "
            f"AND {_EMAIL} AND {_PHONE} AND "
            f"(password_hash IS NULL OR (CHAR_LENGTH(password_hash) BETWEEN 1 AND 512 "
            f"AND {_ascii('password_hash')}))",
            name="optional_text",
        ),
        CheckConstraint("status IN ('active','inactive','locked')", name="status"),
        CheckConstraint(
            "(status <> 'active' OR password_hash IS NOT NULL) AND "
            "(invitation_accepted_at IS NULL OR password_hash IS NOT NULL)",
            name="activation",
        ),
        CheckConstraint(_INVITATION, name="invitation"),
        _TABLE_OPTIONS,
    )

    username: Mapped[str] = mapped_column(String(64))
    real_name: Mapped[str] = mapped_column(String(100))
    nickname: Mapped[str | None] = mapped_column(String(100))
    display_name: Mapped[str | None] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(254))
    phone: Mapped[str | None] = mapped_column(String(16))
    password_hash: Mapped[str | None] = mapped_column(String(512), deferred=True)
    status: Mapped[str] = mapped_column(String(8), default="inactive", server_default="inactive")
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("0"))
    invitation_token_hash: Mapped[str | None] = mapped_column(CHAR(64), deferred=True)
    invitation_issued_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    invitation_expires_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    invitation_sent_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    invitation_accepted_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    invitation_revoked_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    active_key: Mapped[int | None] = mapped_column(TINYINT, Computed(_ACTIVE, persisted=False))


class Organization(UUIDPrimaryKeyMixin, TimestampMixin, RecordStatusMixin, Base):
    """统一组织树，部门仅为节点类型；status 直接继承公共 Mixin。"""

    __tablename__ = "sys_organization"
    __table_args__ = (
        Index("uq_sys_organization_code_active", "organization_code", "active_key", unique=True),
        Index("ix_sys_org_parent_deleted_status", "parent_id", "is_deleted", "status"),
        CheckConstraint("is_deleted IN (0,1)", name="deleted"),
        CheckConstraint(
            "organization_type IN ('group','company','department') AND "
            f"{_identifier('organization_code')} AND {_display('organization_name')}",
            name="type_and_text",
        ),
        CheckConstraint("parent_id IS NULL OR parent_id <> id", name="not_self"),
        CheckConstraint(
            "(organization_type='group' AND parent_id IS NULL) OR organization_type='company' "
            "OR (organization_type='department' AND parent_id IS NOT NULL)",
            name="root",
        ),
        _TABLE_OPTIONS,
    )

    organization_code: Mapped[str] = mapped_column(String(64))
    organization_name: Mapped[str] = mapped_column(String(200))
    organization_type: Mapped[str] = mapped_column(String(32))
    parent_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True, native_uuid=False),
        ForeignKey(
            "sys_organization.id",
            name="fk_sys_org_parent",
            ondelete="RESTRICT",
            onupdate="RESTRICT",
        ),
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("0"))
    active_key: Mapped[int | None] = mapped_column(TINYINT, Computed(_ACTIVE, persisted=False))


class UserOrganization(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """多对多关联历史；两个投影分别保证有效关系及主要归属唯一。"""

    __tablename__ = "sys_user_organization"
    __table_args__ = (
        Index("uq_sys_user_org_active", "user_id", "organization_id", "active_key", unique=True),
        Index("uq_sys_user_org_primary", "primary_user_id", unique=True),
        Index("ix_sys_user_org_user_deleted_primary", "user_id", "is_deleted", "is_primary"),
        Index("ix_sys_user_org_org_deleted_user", "organization_id", "is_deleted", "user_id"),
        CheckConstraint("is_deleted IN (0,1) AND is_primary IN (0,1)", name="flags"),
        _TABLE_OPTIONS,
    )

    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True, native_uuid=False),
        ForeignKey(
            "sys_user.id", name="fk_sys_user_org_user", ondelete="RESTRICT", onupdate="RESTRICT"
        ),
    )
    organization_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True, native_uuid=False),
        ForeignKey(
            "sys_organization.id",
            name="fk_sys_user_org_org",
            ondelete="RESTRICT",
            onupdate="RESTRICT",
        ),
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("0"))
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("0"))
    active_key: Mapped[int | None] = mapped_column(TINYINT, Computed(_ACTIVE, persisted=False))
    primary_user_id: Mapped[str | None] = mapped_column(
        CHAR(32),
        Computed(
            "CASE WHEN is_deleted=0 AND is_primary=1 THEN user_id ELSE NULL END", persisted=False
        ),
    )
