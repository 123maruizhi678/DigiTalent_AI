"""统一同步数据库资源；提交事务由业务调用方负责。"""

import logging
from collections.abc import Iterator

from fastapi import Request
from sqlalchemy import URL, create_engine, text
from sqlalchemy.exc import DBAPIError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings

logger = logging.getLogger(__name__)


class DatabaseError(RuntimeError):
    """安全诊断，只携带预定义错误分类。"""


def diagnose(error: SQLAlchemyError) -> str:
    """提取驱动数字错误码，不记录原始异常、SQL 或连接凭据。"""
    code = None
    if isinstance(error, DBAPIError) and error.orig.args:
        code = error.orig.args[0]
    return {
        1045: "authentication_failed",
        1049: "database_not_found",
        2003: "connection_failed",
        2013: "connection_lost",
    }.get(code, "database_unavailable")


class Database:
    """每个应用生命周期独享 Engine 和工厂；构造时不建立网络连接。"""

    def __init__(self, settings: Settings):
        self.configured = bool(settings.MYSQL_USER and settings.MYSQL_DATABASE)
        self.closed = False
        try:
            self.engine = create_engine(
                URL.create(
                    "mysql+pymysql",
                    username=settings.MYSQL_USER,
                    password=settings.MYSQL_PASSWORD.get_secret_value(),
                    host=settings.MYSQL_HOST,
                    port=settings.MYSQL_PORT,
                    database=settings.MYSQL_DATABASE,
                    query={"charset": "utf8mb4"},
                ),
                pool_size=settings.MYSQL_POOL_SIZE,
                max_overflow=settings.MYSQL_MAX_OVERFLOW,
                pool_timeout=settings.MYSQL_POOL_TIMEOUT,
                pool_recycle=settings.MYSQL_POOL_RECYCLE,
                pool_pre_ping=True,
                connect_args={
                    "connect_timeout": settings.MYSQL_CONNECT_TIMEOUT,
                    "read_timeout": settings.MYSQL_CONNECT_TIMEOUT,
                    "write_timeout": settings.MYSQL_CONNECT_TIMEOUT,
                },
                hide_parameters=True,
            )
        except Exception:
            logger.error("数据库初始化失败：engine_initialization_failed")
            raise DatabaseError("engine_initialization_failed") from None
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)

    def check(self) -> str | None:
        """实际 SELECT 1；连接上下文保证成功和失败路径均归还连接。"""
        if self.closed or not self.configured:
            reason = "database_closed" if self.closed else "database_not_configured"
            logger.warning("数据库检查失败：%s", reason)
            return reason
        try:
            with self.engine.connect() as connection:
                if connection.execute(text("SELECT 1")).scalar_one() != 1:
                    return "unexpected_result"
        except SQLAlchemyError as error:
            reason = diagnose(error)
            logger.warning("数据库检查失败：%s", reason)
            return reason
        return None

    def close(self) -> None:
        """关闭时释放连接池，重复关闭无副作用且不传播驱动异常。"""
        if not self.closed:
            self.closed = True
            try:
                self.engine.dispose()
            except Exception:
                logger.error("数据库资源释放失败：dispose_failed")


def get_session(request: Request) -> Iterator[Session]:
    """同步依赖在线程池运行；同步数据库调用应在 def 路由中执行。

    每个请求独享 Session；业务自行 commit，异常回滚，结束关闭。
    async 路由若使用同步数据库，须将整个数据库操作放入线程池。
    """
    database = request.app.state.database
    if database.closed or not database.configured:
        raise DatabaseError("database_not_available")
    session = database.session_factory()
    try:
        yield session
    except BaseException:
        session.rollback()
        raise
    finally:
        session.close()
