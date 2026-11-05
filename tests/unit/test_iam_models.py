"""IAM 元数据及 MySQL DDL 验证，不连接或修改任何数据库。"""

import subprocess
import sys

import pytest
from sqlalchemy import CheckConstraint, inspect
from sqlalchemy.dialects import mysql
from sqlalchemy.schema import CreateIndex, CreateTable

from app.core.model_mixins import RecordStatus, RecordStatusMixin, RecordStatusType
from app.core.orm import Base
from app.models import register_models


@pytest.fixture
def tables():
    register_models()
    return [
        Base.metadata.tables[name]
        for name in ("sys_user", "sys_organization", "sys_user_organization")
    ]


def test_registration_fresh_process():
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from app.models import register_models; "
            "from app.core.orm import Base; register_models(); register_models(); "
            "assert set(Base.metadata.tables) == "
            "{'sys_user', 'sys_organization', 'sys_user_organization', "
            "'sys_role', 'sys_permission', 'sys_user_role', 'sys_role_permission', 'sys_data_scope'}",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_exact_fields(tables):
    expected = [
        "id username real_name nickname display_name email phone password_hash status is_deleted "
        "created_at updated_at invitation_token_hash invitation_issued_at invitation_expires_at "
        "invitation_sent_at invitation_accepted_at invitation_revoked_at active_key",
        "id organization_code organization_name organization_type parent_id status is_deleted "
        "created_at updated_at active_key",
        "id user_id organization_id is_primary is_deleted created_at updated_at active_key primary_user_id",
    ]
    for table, names in zip(tables, expected, strict=True):
        assert set(table.c.keys()) == set(names.split())
        assert table.metadata is Base.metadata


def test_constraint_counts_and_mysql_ddl(tables):
    assert [len(t.c) for t in tables] == [19, 10, 9]
    assert [sum(isinstance(c, CheckConstraint) for c in t.constraints) for t in tables] == [6, 5, 1]
    assert sum(len(t.foreign_keys) for t in tables) == 3
    assert sum(i.unique for t in tables for i in t.indexes) == 7
    assert sum(not i.unique for t in tables for i in t.indexes) == 4
    for table in tables:
        ddl = str(CreateTable(table).compile(dialect=mysql.dialect()))
        assert "CHAR(32)" in ddl
        assert "DATETIME(6)" in ddl
        assert "VIRTUAL" in ddl
        assert "utf8mb4_0900_bin" in ddl
        for index in table.indexes:
            assert index.name in str(CreateIndex(index).compile(dialect=mysql.dialect()))
        for fk in table.foreign_keys:
            assert fk.ondelete == fk.onupdate == "RESTRICT"
            assert fk.column.table in tables


def test_defaults_generated_and_sensitive_fields(tables):
    from app.models.iam import Organization, User

    user, org, link = tables
    assert user.c.status.default.arg == "inactive"
    assert user.c.status.server_default.arg == "inactive"
    assert isinstance(org.c.status.type, RecordStatusType)
    assert org.c.status.default.arg is RecordStatus.ACTIVE
    # 声明式映射会将继承的 mixin 字段复制为模型自己的 InstrumentedAttribute。
    assert RecordStatusMixin in Organization.__bases__
    assert "status" not in Organization.__annotations__
    assert inspect(Organization).attrs.status.columns[0] is org.c.status
    assert org.c.status.server_default.arg == "active"
    assert not org.c.status.nullable
    assert inspect(User).attrs.password_hash.deferred
    assert inspect(User).attrs.invitation_token_hash.deferred
    for table in tables:
        assert table.c.is_deleted.default.arg is False
        assert str(table.c.is_deleted.server_default.arg) == "0"
        assert not table.c.is_deleted.nullable
        assert (
            str(table.c.active_key.computed.sqltext)
            == "CASE WHEN is_deleted=0 THEN 1 ELSE NULL END"
        )
        assert table.c.active_key.computed.persisted is False
    assert link.c.is_primary.default.arg is False
    assert str(link.c.primary_user_id.computed.sqltext) == (
        "CASE WHEN is_deleted=0 AND is_primary=1 THEN user_id ELSE NULL END"
    )
