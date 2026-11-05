"""数据库基础设施受控测试；不冒充真实 MySQL 集成验证。"""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.core.config import Settings
from app.core.database import Database, get_session
from app.main import app


@pytest.mark.parametrize(
    "field,value",
    [
        ("MYSQL_PORT", 0),
        ("MYSQL_PORT", 65536),
        ("MYSQL_POOL_SIZE", 0),
        ("MYSQL_MAX_OVERFLOW", -1),
        ("MYSQL_POOL_TIMEOUT", 0),
        ("MYSQL_POOL_RECYCLE", 0),
        ("MYSQL_CONNECT_TIMEOUT", 61),
    ],
)
def test_invalid_config(field, value):
    with pytest.raises(ValueError):
        Settings(_env_file=None, **{field: value})


def settings():
    return Settings(
        _env_file=None, MYSQL_USER="test", MYSQL_DATABASE="test", MYSQL_PASSWORD="fake@:/secret"
    )


def test_engine_configuration_and_close():
    database = Database(settings())
    assert database.engine.url.password == "fake@:/secret"
    assert "fake@:/secret" not in repr(database.engine)
    assert database.engine.pool.size() == 5
    assert database.engine.pool._max_overflow == 10
    assert database.engine.pool.timeout() == 30
    assert database.engine.pool._recycle == 1800
    assert database.engine.pool._pre_ping
    dispose = MagicMock()
    database.engine.dispose = dispose
    database.close()
    database.close()
    dispose.assert_called_once()


def test_check_executes_and_returns_connection():
    database = Database(settings())
    connection = MagicMock()
    database.engine.connect = MagicMock(return_value=connection)
    connection.__enter__.return_value.execute.return_value.scalar_one.return_value = 1
    assert database.check() is None
    statement = connection.__enter__.return_value.execute.call_args.args[0]
    assert str(statement) == "SELECT 1"
    connection.__exit__.assert_called_once()
    database.close()
    assert database.check() == "database_closed"


def test_failure_is_diagnosable_and_safe(caplog):
    database = Database(settings())
    database.engine.connect = MagicMock(
        side_effect=OperationalError(
            "secret SQL", {}, Exception(1045, "fake@:/secret mysql://private")
        )
    )
    assert database.check() == "authentication_failed"
    assert "authentication_failed" in caplog.text
    assert "fake@:/secret" not in caplog.text
    assert "mysql://" not in caplog.text
    database.close()


@pytest.mark.parametrize("fails", [False, True])
def test_check_connection_context_released(fails):
    database = Database(settings())
    connection = MagicMock()
    database.engine.connect = MagicMock(return_value=connection)
    if fails:
        connection.__enter__.return_value.execute.side_effect = OperationalError(
            "", {}, Exception(2003)
        )
    else:
        connection.__enter__.return_value.execute.return_value.scalar_one.return_value = 1
    assert database.check() == ("connection_failed" if fails else None)
    connection.__exit__.assert_called_once()
    database.close()


def test_sessions_unique_closed_rollback_without_commit():
    database = Database(settings())
    sessions = [MagicMock(), MagicMock()]
    database.session_factory = MagicMock(side_effect=sessions)
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(database=database)))
    first = get_session(request)
    second = get_session(request)
    assert next(first) is sessions[0]
    assert next(second) is sessions[1]
    first.close()
    with pytest.raises(RuntimeError):
        second.throw(RuntimeError("failure"))
    for session in sessions:
        session.close.assert_called_once()
        session.rollback.assert_called_once()
        session.commit.assert_not_called()
    database.close()


def test_normal_session_completion():
    session = MagicMock()
    request = SimpleNamespace(
        app=SimpleNamespace(
            state=SimpleNamespace(
                database=SimpleNamespace(
                    closed=False, configured=True, session_factory=lambda: session
                )
            )
        )
    )
    dependency = get_session(request)
    next(dependency)
    with pytest.raises(StopIteration):
        next(dependency)
    session.rollback.assert_not_called()
    session.close.assert_called_once()
    session.commit.assert_not_called()


@pytest.mark.parametrize("reason", [None, "authentication_failed", "database_not_configured"])
def test_health_and_lifecycle(monkeypatch, reason):
    with TestClient(app) as client:
        database = app.state.database
        monkeypatch.setattr(database, "check", lambda: reason)
        response = client.get("/api/v1/health/db")
        assert response.status_code == (503 if reason else 200)
        assert response.json() == {
            "status": "unavailable" if reason else "ok",
            "database": "mysql",
            "reason": reason,
        }
        assert client.get("/api/v1/health").json()["status"] == "ok"
        assert not database.closed
    assert database.closed


def test_real_session_factory():
    database = Database(settings())
    one, two = database.session_factory(), database.session_factory()
    try:
        assert one is not two
        assert one.bind is database.engine
    finally:
        one.close()
        two.close()
        database.close()


def test_initialization_failure_safe(monkeypatch, caplog):
    from app.core import database as module

    monkeypatch.setattr(
        module, "create_engine", MagicMock(side_effect=RuntimeError("fake@:/secret"))
    )
    with pytest.raises(module.DatabaseError, match="engine_initialization_failed") as caught:
        Database(settings())
    assert "fake@:/secret" not in caplog.text + str(caught.value)


def test_close_failure_safe(caplog):
    database = Database(settings())
    database.engine.dispose = MagicMock(side_effect=RuntimeError("fake@:/secret"))
    database.close()
    database.close()
    database.engine.dispose.assert_called_once()
    assert "dispose_failed" in caplog.text
    assert "fake@:/secret" not in caplog.text


def test_config_environment_and_timeout(monkeypatch):
    from app.core import database as module

    monkeypatch.setenv("MYSQL_PORT", "3307")
    monkeypatch.setenv("MYSQL_POOL_SIZE", "7")
    monkeypatch.setenv("MYSQL_PASSWORD", "synthetic-secret")
    configured = settings()
    assert configured.MYSQL_PORT == 3307
    assert configured.MYSQL_POOL_SIZE == 7
    # 显式传入的合成密码优先于环境变量，不泄露到 repr。
    assert "fake@:/secret" not in repr(configured)
    factory = MagicMock()
    monkeypatch.setattr(module, "create_engine", factory)
    Database(configured)
    options = factory.call_args.kwargs
    assert options["connect_args"] == {"connect_timeout": 5, "read_timeout": 5, "write_timeout": 5}
    assert options["hide_parameters"] is True
