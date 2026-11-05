"""P6-IAM-002：RBAC 与基础数据范围声明；不访问数据库或执行授权判断。"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, Computed, ForeignKey, Index, String, Uuid, text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.model_mixins import (
    RecordStatusMixin,
    TimestampMixin,
    UTCDateTime,
    UUIDPrimaryKeyMixin,
)
from app.core.orm import Base
from app.models.iam import User

_OPTIONS = {
    "mysql_engine": "InnoDB",
    "mysql_charset": "utf8mb4",
    "mysql_collate": "utf8mb4_0900_bin",
}
_ACTIVE = "CASE WHEN is_deleted=0 THEN 1 ELSE NULL END"


class AuthorizationRecord(UUIDPrimaryKeyMixin, TimestampMixin, RecordStatusMixin):
    """新增授权表公共组合；停用保留唯一名额，删除释放名额。"""

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("0"))
    active_key: Mapped[int | None] = mapped_column(TINYINT, Computed(_ACTIVE, persisted=False))


class Role(AuthorizationRecord, Base):
    """角色定义；名称允许重复，编码仅未删除记录唯一。"""

    __tablename__ = "sys_role"
    __table_args__ = (
        Index("uq_sys_role_code_active", "role_code", "active_key", unique=True),
        Index("ix_sys_role_deleted_status", "is_deleted", "status"),
        CheckConstraint("is_deleted IN (0,1)", name="deleted"),
        CheckConstraint(
            "CHAR_LENGTH(TRIM(role_code)) > 0 AND CHAR_LENGTH(TRIM(role_name)) > 0", name="text"
        ),
        _OPTIONS,
    )
    role_code: Mapped[str] = mapped_column(String(64))
    role_name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(String(1000))
    user_links: Mapped[list["UserRole"]] = relationship(
        back_populates="role", passive_deletes="all"
    )
    permission_links: Mapped[list["RolePermission"]] = relationship(
        back_populates="role", passive_deletes="all"
    )


class Permission(AuthorizationRecord, Base):
    """资源操作权限；permission_code 同时作为稳定权限标识，无隐式层级继承。"""

    __tablename__ = "sys_permission"
    __table_args__ = (
        Index("uq_sys_permission_code_active", "permission_code", "active_key", unique=True),
        Index(
            "ix_sys_permission_resource_action", "resource_type", "action", "is_deleted", "status"
        ),
        CheckConstraint("is_deleted IN (0,1)", name="deleted"),
        CheckConstraint(
            "CHAR_LENGTH(TRIM(permission_code)) > 0 AND CHAR_LENGTH(TRIM(permission_name)) > 0 AND CHAR_LENGTH(TRIM(resource_type)) > 0 AND CHAR_LENGTH(TRIM(action)) > 0",
            name="text",
        ),
        _OPTIONS,
    )
    permission_code: Mapped[str] = mapped_column(String(128))
    permission_name: Mapped[str] = mapped_column(String(200))
    resource_type: Mapped[str] = mapped_column(String(128))
    action: Mapped[str] = mapped_column(String(64))
    role_links: Mapped[list["RolePermission"]] = relationship(
        back_populates="permission", passive_deletes="all"
    )


class UserRole(AuthorizationRecord, Base):
    """用户与角色多对多；关系本身具有独立状态和历史。"""

    __tablename__ = "sys_user_role"
    __table_args__ = (
        Index("uq_sys_user_role_active", "user_id", "role_id", "active_key", unique=True),
        Index("ix_sys_user_role_role", "role_id", "is_deleted", "status", "user_id"),
        CheckConstraint("is_deleted IN (0,1)", name="deleted"),
        _OPTIONS,
    )
    user_id: Mapped[UUID] = mapped_column(
        Uuid(native_uuid=False), ForeignKey("sys_user.id", ondelete="RESTRICT", onupdate="RESTRICT")
    )
    role_id: Mapped[UUID] = mapped_column(
        Uuid(native_uuid=False), ForeignKey("sys_role.id", ondelete="RESTRICT", onupdate="RESTRICT")
    )
    user: Mapped[User] = relationship(passive_deletes="all")
    role: Mapped[Role] = relationship(back_populates="user_links", passive_deletes="all")


class RolePermission(AuthorizationRecord, Base):
    """角色与权限多对多；取消授权保留删除历史。"""

    __tablename__ = "sys_role_permission"
    __table_args__ = (
        Index(
            "uq_sys_role_permission_active", "role_id", "permission_id", "active_key", unique=True
        ),
        Index(
            "ix_sys_role_permission_permission", "permission_id", "is_deleted", "status", "role_id"
        ),
        CheckConstraint("is_deleted IN (0,1)", name="deleted"),
        _OPTIONS,
    )
    role_id: Mapped[UUID] = mapped_column(
        Uuid(native_uuid=False), ForeignKey("sys_role.id", ondelete="RESTRICT", onupdate="RESTRICT")
    )
    permission_id: Mapped[UUID] = mapped_column(
        Uuid(native_uuid=False),
        ForeignKey("sys_permission.id", ondelete="RESTRICT", onupdate="RESTRICT"),
    )
    role: Mapped[Role] = relationship(back_populates="permission_links", passive_deletes="all")
    permission: Mapped[Permission] = relationship(
        back_populates="role_links", passive_deletes="all"
    )


class DataScope(AuthorizationRecord, Base):
    """独立数据范围基础记录；多态主体及目标存在性须由后续 Service 校验。"""

    __tablename__ = "sys_data_scope"
    __table_args__ = (
        Index(
            "uq_sys_data_scope_active",
            "subject_type",
            "subject_id",
            "scope_type",
            "scope_value",
            "active_key",
            unique=True,
        ),
        Index("ix_sys_data_scope_subject", "subject_type", "subject_id", "is_deleted", "status"),
        CheckConstraint("is_deleted IN (0,1)", name="deleted"),
        CheckConstraint("subject_type IN ('user','role')", name="subject"),
        CheckConstraint("scope_type IN ('all','dept','self','project')", name="scope"),
        CheckConstraint(
            "(scope_type IN ('all','self') AND scope_value = '') OR (scope_type IN ('dept','project') AND CHAR_LENGTH(TRIM(scope_value)) > 0)",
            name="value",
        ),
        CheckConstraint(
            "expires_at IS NULL OR (starts_at IS NOT NULL AND expires_at > starts_at)",
            name="period",
        ),
        _OPTIONS,
    )
    subject_type: Mapped[str] = mapped_column(String(16))
    subject_id: Mapped[UUID] = mapped_column(Uuid(native_uuid=False))
    scope_type: Mapped[str] = mapped_column(String(16))
    scope_value: Mapped[str] = mapped_column(String(128), default="", server_default="")
    starts_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    expires_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
