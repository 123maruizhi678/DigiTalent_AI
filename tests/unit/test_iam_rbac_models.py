"""RBAC 映射及安全约束静态验证；不连接数据库。"""

from sqlalchemy import CheckConstraint, inspect
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import configure_mappers
from sqlalchemy.schema import CreateTable

from app.core.model_mixins import (
    RecordStatus,
    RecordStatusMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)
from app.core.orm import Base
from app.models import register_models
from app.models.iam_rbac import DataScope, Permission, Role, RolePermission, UserRole

MODELS = (Role, Permission, UserRole, RolePermission, DataScope)


def test_approved_check_expressions():
    expected = {
        Role: {"text": "CHAR_LENGTH(TRIM(role_code)) > 0 AND CHAR_LENGTH(TRIM(role_name)) > 0"},
        Permission: {
            "text": " AND ".join(
                f"CHAR_LENGTH(TRIM({name})) > 0"
                for name in ("permission_code", "permission_name", "resource_type", "action")
            )
        },
        UserRole: {},
        RolePermission: {},
        DataScope: {
            "subject": "subject_type IN ('user','role')",
            "scope": "scope_type IN ('all','dept','self','project')",
            "value": "(scope_type IN ('all','self') AND scope_value = '') OR (scope_type IN ('dept','project') AND CHAR_LENGTH(TRIM(scope_value)) > 0)",
            "period": "expires_at IS NULL OR (starts_at IS NOT NULL AND expires_at > starts_at)",
        },
    }
    for cls, checks in expected.items():
        checks = checks | {
            "deleted": "is_deleted IN (0,1)",
            "record_status": "status IN ('active', 'inactive')",
        }
        actual = {
            c.name: str(
                c.sqltext.compile(
                    dialect=mysql.dialect(),
                    compile_kwargs={
                        "literal_binds": True,
                        "include_table": False,
                    },
                )
            )
            for c in cls.__table__.constraints
            if isinstance(c, CheckConstraint)
        }
        assert actual == {f"ck_{cls.__tablename__}_{name}": value for name, value in checks.items()}


def test_registration_relationships_and_storage():
    register_models()
    configure_mappers()
    assert inspect(UserRole).relationships.user.mapper.class_.__name__ == "User"
    assert inspect(UserRole).relationships.role.back_populates == "user_links"
    assert inspect(RolePermission).relationships.permission.back_populates == "role_links"
    assert sum(len(cls.__table__.foreign_keys) for cls in MODELS) == 4
    for cls in MODELS:
        assert issubclass(cls, RecordStatusMixin)
        table = cls.__table__
        ddl = str(CreateTable(table).compile(dialect=mysql.dialect()))
        assert "CHAR(32)" in ddl and "DATETIME(6)" in ddl
        assert "InnoDB" in ddl and "utf8mb4_0900_bin" in ddl
        assert table.c.active_key.computed.persisted is False
        unique = [i for i in table.indexes if i.unique]
        assert len(unique) == 1 and "active_key" in unique[0].columns
        assert table.c.is_deleted.default.arg is False
        assert all(fk.ondelete == fk.onupdate == "RESTRICT" for fk in table.foreign_keys)
        checks = {c.name for c in table.constraints if isinstance(c, CheckConstraint)}
        assert f"ck_{table.name}_deleted" in checks
        assert f"ck_{table.name}_record_status" in checks


def test_data_scope_is_separate_and_has_period_checks():
    table = DataScope.__table__
    checks = {c.name: str(c.sqltext) for c in table.constraints if isinstance(c, CheckConstraint)}
    assert "'all','dept','self','project'" in checks["ck_sys_data_scope_scope"]
    assert "expires_at > starts_at" in checks["ck_sys_data_scope_period"]
    assert "data_scope" not in Role.__table__.c
    assert "parent_id" not in Permission.__table__.c


def test_approved_field_contract_and_common_mixins():
    """以开发记录规格为独立预期，避免 ORM 和 SQL 同时漂移仍通过。"""
    specifications = {
        Role: {
            "role_code": "VARCHAR(64)",
            "role_name": "VARCHAR(200)",
            "description": "VARCHAR(1000)",
        },
        Permission: {
            "permission_code": "VARCHAR(128)",
            "permission_name": "VARCHAR(200)",
            "resource_type": "VARCHAR(128)",
            "action": "VARCHAR(64)",
        },
        UserRole: {"user_id": "CHAR(32)", "role_id": "CHAR(32)"},
        RolePermission: {"role_id": "CHAR(32)", "permission_id": "CHAR(32)"},
        DataScope: {
            "subject_type": "VARCHAR(16)",
            "subject_id": "CHAR(32)",
            "scope_type": "VARCHAR(16)",
            "scope_value": "VARCHAR(128)",
            "starts_at": "DATETIME(6)",
            "expires_at": "DATETIME(6)",
        },
    }
    common = {
        "id": "CHAR(32)",
        "created_at": "DATETIME(6)",
        "updated_at": "DATETIME(6)",
        "status": "VARCHAR(8)",
        "is_deleted": "BOOL",
        "active_key": "TINYINT",
    }
    for cls, business in specifications.items():
        table = cls.__table__
        assert table.metadata is Base.metadata
        for mixin in (UUIDPrimaryKeyMixin, TimestampMixin, RecordStatusMixin):
            assert issubclass(cls, mixin)
        assert set(table.c.keys()) == set(common | business)
        assert list(table.primary_key.columns.keys()) == ["id"]
        for name, expected in (common | business).items():
            column = table.c[name]
            assert column.type.compile(dialect=mysql.dialect()) == expected
            assert column.nullable == (
                name in {"description", "starts_at", "expires_at", "active_key"}
            )
        assert table.c.status.default.arg is RecordStatus.ACTIVE
        assert table.c.status.server_default.arg == "active"
        assert str(table.c.is_deleted.server_default.arg) == "0"
        assert str(table.c.active_key.computed.sqltext) == (
            "CASE WHEN is_deleted=0 THEN 1 ELSE NULL END"
        )
        for name in ("id", "created_at", "updated_at"):
            assert callable(table.c[name].default.arg)
            assert table.c[name].server_default is None
        assert table.c.created_at.onupdate is None
        assert callable(table.c.updated_at.onupdate.arg)
        for name in business:
            column = table.c[name]
            if name == "scope_value":
                assert column.default.arg == column.server_default.arg == ""
            else:
                assert column.default is column.server_default is None


def test_relationship_targets_pairs_and_no_delete_cascade():
    expected = {
        Role: {
            "user_links": (UserRole, "role", True),
            "permission_links": (RolePermission, "role", True),
        },
        Permission: {"role_links": (RolePermission, "permission", True)},
        UserRole: {"user": (None, None, False), "role": (Role, "user_links", False)},
        RolePermission: {
            "role": (Role, "permission_links", False),
            "permission": (Permission, "role_links", False),
        },
        DataScope: {},
    }
    from app.models.iam import User

    expected[UserRole]["user"] = (User, None, False)
    for cls, relationships in expected.items():
        mapped = inspect(cls).relationships
        assert set(mapped.keys()) == set(relationships)
        for name, (target, reverse, collection) in relationships.items():
            relation = mapped[name]
            assert relation.mapper.class_ is target
            assert relation.back_populates == reverse
            assert relation.uselist is collection
            assert relation.passive_deletes == "all"
            assert not {"delete", "delete-orphan"} & set(relation.cascade)
            # 关系返回原始记录，状态和逻辑删除过滤属于后续服务职责。
            assert "is_deleted" not in str(relation.primaryjoin)
            assert "status" not in str(relation.primaryjoin)
    assert not DataScope.__table__.foreign_keys


def test_approved_unique_keys_and_foreign_key_targets():
    keys = {
        Role: ("role_code", "active_key"),
        Permission: ("permission_code", "active_key"),
        UserRole: ("user_id", "role_id", "active_key"),
        RolePermission: ("role_id", "permission_id", "active_key"),
        DataScope: ("subject_type", "subject_id", "scope_type", "scope_value", "active_key"),
    }
    targets = {
        UserRole: {("user_id", "sys_user.id"), ("role_id", "sys_role.id")},
        RolePermission: {("role_id", "sys_role.id"), ("permission_id", "sys_permission.id")},
    }
    for cls, columns in keys.items():
        assert {tuple(i.columns.keys()) for i in cls.__table__.indexes if i.unique} == {columns}
        assert {
            (fk.parent.name, fk.target_fullname) for fk in cls.__table__.foreign_keys
        } == targets.get(cls, set())
