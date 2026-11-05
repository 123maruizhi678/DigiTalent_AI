"""公共模型隔离验收；所有测试表在 fixture 结束后从唯一 metadata 移除。"""

from uuid import UUID

import pytest
from sqlalchemy import ForeignKey, Integer, String, Uuid, inspect
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import Mapped, mapped_column, registry
from sqlalchemy.schema import CreateTable

from app.core.model_mixins import (
    RecordStatusMixin,
    TimestampMixin,
    UTCDateTime,
    UUIDPrimaryKeyMixin,
)
from app.core.orm import Base
from app.models import register_models


@pytest.fixture
def models():
    # 测试 registry 仅隔离 mapper 生命周期，metadata 仍为生产唯一入口。
    test_registry = registry(metadata=Base.metadata)

    class TestBase(Base):
        __abstract__ = True
        registry = test_registry
        _sa_registry = test_registry

    class Example(UUIDPrimaryKeyMixin, TimestampMixin, RecordStatusMixin, TestBase):
        __tablename__ = "test_common_example"
        name: Mapped[str] = mapped_column(String(30))

    class Child(UUIDPrimaryKeyMixin, TestBase):
        __tablename__ = "test_common_child"
        parent_id: Mapped[UUID] = mapped_column(
            Uuid(as_uuid=True, native_uuid=False), ForeignKey("test_common_example.id")
        )

    class TimeOnly(TimestampMixin, TestBase):
        __tablename__ = "test_time_only"
        key: Mapped[int] = mapped_column(Integer, primary_key=True)

    class StatusOnly(RecordStatusMixin, TestBase):
        __tablename__ = "test_status_only"
        key: Mapped[int] = mapped_column(Integer, primary_key=True)

    classes = (Example, Child, TimeOnly, StatusOnly)
    tables = [cls.__table__ for cls in classes]
    try:
        yield classes
    finally:
        test_registry.dispose()
        for table in reversed(tables):
            Base.metadata.remove(table)


def test_base_and_composition(models):
    example, child, time_only, status_only = models
    register_models()
    assert {"sys_user", "sys_organization", "sys_user_organization"} <= set(Base.metadata.tables)
    assert inspect(Base, raiseerr=False) is None
    assert set(example.__table__.c.keys()) == {"id", "name", "created_at", "updated_at", "status"}
    assert set(child.__table__.c.keys()) == {"id", "parent_id"}
    assert set(time_only.__table__.c.keys()) == {"key", "created_at", "updated_at"}
    assert set(status_only.__table__.c.keys()) == {"key", "status"}
    assert all(cls.__table__.metadata is Base.metadata for cls in models)
    assert all(issubclass(cls, Base) for cls in models)


def test_mysql_ddl_compilation(models):
    ddl = str(CreateTable(models[0].__table__).compile(dialect=mysql.dialect()))
    assert "CHAR(32)" in ddl
    assert ddl.count("DATETIME(6)") == 2
    assert "VARCHAR(8)" in ddl
    assert "CHECK (status IN ('active', 'inactive'))" in ddl
    assert "PRIMARY KEY (id)" in ddl
    assert UTCDateTime().process_bind_param(None, mysql.dialect()) is None


def test_model_metadata_registration(models):
    register_models()
    register_models()
    for cls in models:
        assert Base.metadata.tables[cls.__tablename__] is cls.__table__
    child = models[1].__table__
    assert next(iter(child.c.parent_id.foreign_keys)).column is models[0].__table__.c.id
    assert {"sys_user", "sys_organization", "sys_user_organization"} <= set(Base.metadata.tables)
