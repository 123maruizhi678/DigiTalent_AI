# SQL 执行说明

- `init.sql`：人工维护的 P6-IAM-001 三表和三个触发器，MySQL 8.0.17+，环境基线 8.0.44。仅用于授权的新建空白隔离库；使用支持 DELIMITER 的 mysql 客户端。无建库语句，无业务种子，不可重复应用于已有同名对象的库。
- `changes/`：存量结构变更按日期与用途命名；本轮没有存量变更授权，不新增变更 SQL。
- `test_common_models.sql`：公共 Mixin 测试辅助表，仅由授权人员在独立测试库人工准备。不是业务初始化内容。

执行前由审核人与执行人分别确认目标实例、库名、隔离账号、MySQL 版本、严格 SQL 模式、utf8mb4_0900_bin、CHECK 执行及触发器权限。记录 SHOW CREATE TABLE、SHOW INDEX、information_schema 约束与触发器定义。UUID/时间无数据库默认，原始 SQL 必须显式提供。

本轮未执行以上文件。DDL 有隐式提交，不得以事务回滚作为部署回退保证；存量库须另审差异与备份恢复方案。触发器不替代 Service 的树无环、父子类型矩阵、用户删除关联及组织删除阻止事务。

经用户明确授权、人工准备并核实隔离库后，运行：

```powershell
conda run -n feiyu python -m pytest -q tests/mysql_orm_check.py tests/mysql_iam_check.py --mysql-test-config <独立配置绝对路径> --mysql-test-database <已核实的_test库名> --mysql-test-authorized
```

独立配置复用统一 Settings 的 MYSQL_* 字段，敏感凭据不得入库。库名后缀校验不能代替人工隔离确认；不得把业务库改名后用于测试。测试只执行 DML/查询、不建表，每个用例使用外层事务回滚，测试辅助表须为空。默认 pytest 不收集这两个显式验收文件；它们不是跳过用例，必须单独运行并记录真实结果。
