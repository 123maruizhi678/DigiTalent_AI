"""手工真实 MySQL 只读集成检查，不进入 pytest 自动收集。

从项目根目录执行：
conda run -n feiyu python -m tests.mysql_integration_check

复用统一 Settings 和应用数据库生命周期，仅执行 SELECT 1 和健康接口检查；
不创建或修改数据库、表、数据，不执行迁移，不输出密码或完整连接字符串。
退出码：0 表示检查通过，2 表示检查失败。
"""

from types import SimpleNamespace

from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import ConfigurationError
from app.core.database import DatabaseError, diagnose, get_session


class IntegrationCheckError(RuntimeError):
    """仅携带脚本预定义的安全错误分类。"""


def main() -> int:
    """实际验证连接、请求 Session、健康接口及 Engine 关闭。"""
    try:
        # 延迟加载应用，将真实配置读取错误纳入安全诊断。
        from app.main import app

        with TestClient(app, raise_server_exceptions=False) as client:
            database = app.state.database
            reason = database.check()
            if reason:
                raise IntegrationCheckError(reason)

            dependency = get_session(SimpleNamespace(app=app))
            try:
                session = next(dependency)
                if session.execute(text("SELECT 1")).scalar_one() != 1:
                    raise IntegrationCheckError("unexpected_session_result")
            finally:
                dependency.close()

            response = client.get("/api/v1/health/db")
            if response.status_code != 200 or response.json() != {
                "status": "ok",
                "database": "mysql",
                "reason": None,
            }:
                raise IntegrationCheckError("database_health_failed")

            response = client.get("/api/v1/health")
            if response.status_code != 200 or response.json().get("status") != "ok":
                raise IntegrationCheckError("process_health_failed")

        if not database.closed:
            raise IntegrationCheckError("database_lifecycle_failed")
    except ConfigurationError:
        reason = "configuration_invalid"
    except DatabaseError:
        reason = "database_initialization_or_session_failed"
    except SQLAlchemyError as error:
        reason = diagnose(error)
    except IntegrationCheckError as error:
        reason = str(error)
    except Exception:
        # 不输出原始异常或堆栈，防止驱动及配置错误携带凭据。
        reason = "unexpected_check_failure"
    else:
        print("REAL_MYSQL_RESULT=SELECT_1_SESSION_HEALTH_LIFECYCLE_OK")
        return 0

    print(f"REAL_MYSQL_RESULT={reason}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
