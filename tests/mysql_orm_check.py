"""显式 MySQL 公共模型验收，人工准备测试结构后运行。"""

from datetime import UTC, datetime, timedelta, timezone
from enum import StrEnum
from uuid import UUID

import pytest
from fastapi.encoders import jsonable_encoder
from sqlalchemy import text, update
from sqlalchemy.exc import IntegrityError, StatementError
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.database import Database
from app.core.model_mixins import RecordStatus
from tests.unit import test_orm


@pytest.fixture
def models():
    yield from test_orm.models.__wrapped__()


@pytest.fixture
def database(request):
    config_path = request.config.getoption("--mysql-test-config")
    expected = request.config.getoption("--mysql-test-database")
    if not request.config.getoption("--mysql-test-authorized") or not config_path or not expected:
        pytest.fail("需要明确写入授权、独立测试配置文件及已确认的测试库名")
    settings = Settings(_env_file=config_path)
    assert settings.MYSQL_DATABASE == expected and expected.endswith("_test")
    assert expected != "agent_service"
    resource = Database(settings)
    try:
        with resource.engine.connect() as connection:
            assert connection.execute(text("SELECT DATABASE()")).scalar_one() == expected
            version = connection.execute(text("SELECT VERSION()")).scalar_one()
            assert version.startswith("8.0.") and int(version.split(".")[2].split("-")[0]) >= 17
            mode = connection.execute(text("SELECT @@sql_mode")).scalar_one()
            assert "STRICT_ALL_TABLES" in mode or "STRICT_TRANS_TABLES" in mode
            connection.rollback()
            transaction = connection.begin()
            try:
                yield connection
            finally:
                if transaction.is_active:
                    transaction.rollback()
    finally:
        resource.close()


def test_uuid_roundtrip_json_and_foreign_key(database, models):
    example, child, _, _ = models
    with Session(database) as session:
        rows = [example(name=str(index)) for index in range(100)]
        session.add_all(rows)
        session.flush()
        ids = [row.id for row in rows]
        assert len(set(ids)) == 100
        assert all(isinstance(value, UUID) and value.version == 4 for value in ids)
        session.add(child(parent_id=ids[0]))
        session.commit()
        session.expunge_all()
        assert session.get(example, ids[0]).id == ids[0]
        assert session.query(child).one().parent_id == ids[0]
        assert jsonable_encoder({"id": ids[0]}) == {"id": str(ids[0])}
        raw = session.execute(text("SELECT id FROM test_common_example")).scalars().all()
        assert set(raw) == {value.hex for value in ids}


def test_timestamps_create_update_and_precision(database, models):
    example = models[0]
    with Session(database) as session:
        row = example(name="before")
        session.add(row)
        session.commit()
        session.refresh(row)
        created, updated = row.created_at, row.updated_at
        assert created.tzinfo is UTC and updated.tzinfo is UTC
        # 设置确定的旧值，验证 onupdate，避免依赖 sleep 或时钟精度。
        row.updated_at = updated - timedelta(days=1)
        session.commit()
        row.name = "after"
        session.commit()
        session.refresh(row)
        assert row.created_at == created
        assert row.updated_at > updated - timedelta(days=1)
        converted = datetime(2026, 1, 2, 12, 0, 0, 123456, timezone(timedelta(hours=8)))
        row.created_at = converted
        session.commit()
        session.refresh(row)
        assert row.created_at == converted.astimezone(UTC)
        assert row.created_at.microsecond == 123456
        session.execute(update(example).where(example.id == row.id).values(name="core update"))
        session.commit()
        session.refresh(row)
        assert row.created_at == converted.astimezone(UTC)


def test_independent_mixins_write_and_query(database, models):
    with Session(database) as session:
        session.add_all([models[2](key=1), models[3](key=1)])
        session.commit()
        assert session.get(models[2], 1).created_at.tzinfo is UTC
        assert session.get(models[3], 1).status is RecordStatus.ACTIVE


def test_naive_time_rejected(database, models):
    with Session(database) as session:
        session.add(models[0](name="bad", created_at=datetime(2026, 1, 1)))
        with pytest.raises(StatementError, match="时区"):
            session.flush()


def test_status_defaults_and_valid_change(database, models):
    with Session(database) as session:
        row = models[0](name="status")
        session.add(row)
        session.commit()
        session.refresh(row)
        assert row.status is RecordStatus.ACTIVE
        row.status = RecordStatus.INACTIVE
        session.commit()
        session.refresh(row)
        assert row.status is RecordStatus.INACTIVE


@pytest.mark.parametrize("invalid", ["unknown", "active", 1])
def test_status_python_constraint(database, models, invalid):
    with Session(database) as session:
        session.add(models[0](name="bad", status=invalid))
        with pytest.raises(StatementError, match="RecordStatus"):
            session.flush()


def test_business_status_not_interchangeable(database, models):
    class AccountStatus(StrEnum):
        ACTIVE = "active"

    with Session(database) as session:
        session.add(models[0](name="bad", status=AccountStatus.ACTIVE))
        with pytest.raises(StatementError, match="RecordStatus"):
            session.flush()


def test_status_database_constraint_and_server_default(database, models):
    with database.begin_nested() as conn:
        conn.execute(text("INSERT INTO test_status_only (`key`) VALUES (1)"))
        assert conn.execute(text("SELECT status FROM test_status_only")).scalar_one() == "active"
        with pytest.raises(IntegrityError):
            conn.execute(text("INSERT INTO test_status_only (`key`, status) VALUES (2, 'bad')"))
