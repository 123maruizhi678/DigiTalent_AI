"""正式模型唯一注册入口；禁止导入测试模型或在导入时访问数据库。"""


def register_models() -> None:
    """加载全部正式模型，将表定义注册到公共 Base.metadata；不执行数据库操作。

    在此显式导入公共实体、IAM、人才档案、Agent、Workflow
    模型模块；各模块只从 app.core.orm 导入 Base。不要动态扫描目录或吞掉导入错误。
    """
    from app.models import (
        iam,  # noqa: F401
        iam_rbac,  # noqa: F401
    )
