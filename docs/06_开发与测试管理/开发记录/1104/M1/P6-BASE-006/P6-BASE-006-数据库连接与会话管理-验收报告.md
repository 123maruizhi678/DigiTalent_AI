# P6-BASE-006：MySQL 连接与会话管理验收报告

日期：2026-11-04
最终状态：**部分完成**。基础设施和自动化回归已完成；真实 MySQL 验收受缺少有效连接配置阻塞，不能标记已完成。

## 1. 原有实现与工作区

原有 app.main:app、/api/v1 路由、/health 存活检查、统一 Pydantic Settings、日志和异常设施已存在。未发现 Engine、Session 工厂或数据库连接检查。requirements 原先未声明数据库依赖，但 feiyu 已安装 SQLAlchemy 2.1.6 和 PyMySQL 1.2.3。

开始前已有 .env.example、app/core/config.py、tests/unit/test_config.py 等未提交改动，以及未跟踪的 requirements 目录和 tests/api/test_api_paths.py。本次保留其已有内容，增量添加数据库字段、依赖声明和更新路由契约断言。未提交 Git Commit；未读取其他 docs 文档，报告是本次唯一授权的 docs 写入。

## 2. 技术方案与职责

同步 SQLAlchemy + PyMySQL；每个 FastAPI lifespan 创建独立 Database，内部统一管理一个 Engine 和 sessionmaker。Engine 懒连接，启动不主动要求数据库可达；运行时通过检查建立连接。开启 pool_pre_ping，支持回收、池等待和连接超时；读写超时复用连接超时，限制 SELECT 1 等待。

get_session 是同步 yield 依赖，由 FastAPI 在线程池执行，逐请求创建 Session，异常回滚、最终关闭，不自动 commit。正常请求若未提交，关闭 Session 时由 SQLAlchemy 释放并回滚未结束的事务。业务负责明确提交。同步数据库操作应在 def 路由执行；async 路由须把完整同步数据库操作放入线程池。

数据库检查执行 SELECT 1 并归还连接。/api/v1/health 保持原有语义；新增 /api/v1/health/db，成功返回 200，未配置或连接失败返回 503，响应仅含固定状态和原因分类。诊断识别认证失败、库不存在、连接失败、连接中断及通用不可用，不输出原始驱动异常、SQL、密码和 DSN。关闭时在线程池 dispose，重复关闭不重复释放，释放异常只记录固定错误分类。

## 3. 文件清单与共享文件顺序

新增：

| 文件 | 职责 |
| --- | --- |
| app/core/database.py | Engine、工厂、请求 Session 依赖、连接检查、安全诊断和关闭 |
| tests/unit/test_database.py | 配置、连接池、SQL、Session、脱敏和生命周期受控测试 |
| tests/mysql_integration_check.py | 独立真实 MySQL 只读集成检查入口，不经过 pytest 的合成配置隔离 |
| 本报告 | 交付、验证与人工验收记录 |

修改：

| 文件 | 增量职责 |
| --- | --- |
| app/core/config.py | 在现有 Settings 增加 MySQL 字段，复用缓存加载及安全配置错误机制 |
| .env.example | 对应字段中文说明与无真实密码的示例 |
| requirements/base.txt | 在原有未跟踪文件上追加已安装数据库依赖的精确声明 |
| app/main.py | 接入应用级数据库初始化与最终释放，保留入口、路由和中间件 |
| app/api/health.py | 保留存活接口，增加独立数据库就绪检查 |
| tests/unit/test_config.py | 原字段默认值仍逐项断言；新增数据库字段后更新密码保护断言 |
| tests/api/test_health.py | 路由清单覆盖新增接口，保留存活断言 |
| tests/api/test_api_paths.py | 在已有未跟踪文件上更新精确路由集合，保留 Cookie 等原断言 |

共享文件顺序：先读取现有实现和 Git 差异，确认配置与依赖；随后 config.py/.env.example 增量配置，新增数据库模块，再 main.py 生命周期、health.py 就绪接口，最后更新测试契约与检查差异。app/api/router.py 无需修改，现有 health router 自动注册新接口。

## 4. 配置清单

所有字段非必填，Pydantic Field 和 .env.example 均有中文说明；现有配置加载机制保持一致。用户真实 .env 未修改、未输出。.gitignore 已忽略 .env，保留 .env.example。

| 配置 | 中文用途 | 类型 | 默认值 | 合法范围 | 敏感 |
| --- | --- | --- | --- | --- | --- |
| MYSQL_HOST | MySQL 主机地址 | str | 127.0.0.1 | 非空主机名或 IP | 否 |
| MYSQL_PORT | MySQL 端口 | int | 3306 | 1～65535 | 否 |
| MYSQL_USER | 数据库用户名 | str | 空字符串 | 字符串；空表示未配置 | 否 |
| MYSQL_PASSWORD | 数据库密码 | SecretStr | 空字符串 | 字符串，可为空；不裁剪密码 | 是 |
| MYSQL_DATABASE | 数据库名 | str | 空字符串 | 字符串；空表示未配置 | 否 |
| MYSQL_POOL_SIZE | 基础连接数 | int | 5 | 1～100 | 否 |
| MYSQL_MAX_OVERFLOW | 最大额外连接数 | int | 10 | 0～100 | 否 |
| MYSQL_POOL_TIMEOUT | 获取连接等待秒数 | int | 30 | 1～300 | 否 |
| MYSQL_POOL_RECYCLE | 连接回收秒数 | int | 1800 | 1～86400 | 否 |
| MYSQL_CONNECT_TIMEOUT | 连接及驱动读写超时秒数 | int | 5 | 1～60 | 否 |

用户名和数据库名必须同时非空才执行数据库连接检查。密码使用 SecretStr、repr=False，Engine 使用结构化 URL.create 处理特殊字符并设置 hide_parameters。不得直接记录 Settings.model_dump 或 Engine URL；日志遵循仅输出预定义诊断分类的约束。

## 5. 环境和依赖

- Conda：feiyu。
- Python：3.11.18。
- 解释器：D:\anaconda3\envs\feiyu\python.exe。
- pip：26.2.2，位于 D:\anaconda3\envs\feiyu\Lib\site-packages\pip。
- 首次直接 conda activate 未切换当前 PowerShell 解释器；加载 conda shell.powershell hook 后激活成功，复核解释器和 pip 后才执行开发。后续命令显式调用该环境解释器。
- SQLAlchemy==2.1.6、PyMySQL==1.2.3 已安装并成功导入、运行；仅补 requirements/base.txt 声明，没有安装、卸载或升级依赖。
- pytest 8.4.2、Ruff 0.17.3 使用既有安装。

## 6. 命令和结果

环境检查：conda env list；加载 Conda PowerShell hook；conda activate feiyu；python --version；python -c "import sys; print(sys.executable)"；python -m pip --version；python -m pip show SQLAlchemy PyMySQL mysqlclient asyncmy aiomysql pytest ruff。

以下命令中的 python 均实际使用 D:\anaconda3\envs\feiyu\python.exe：

```powershell
& 'D:\anaconda3\envs\feiyu\python.exe' -m ruff check app tests
& 'D:\anaconda3\envs\feiyu\python.exe' -m ruff format --check app tests
& 'D:\anaconda3\envs\feiyu\python.exe' -m pytest -q
& 'D:\anaconda3\envs\feiyu\python.exe' -m tests.mysql_integration_check
```

最终结果：

- Ruff：All checks passed。
- 格式：25 files already formatted。
- pytest：97 passed，0 failed，0 skipped；0.70 秒。
- 含既有 BASE-001/002 相关回归；TestClient 已验证应用启动、Engine 初始化、关闭与释放。
- 新增受控数据库测试覆盖非法配置、环境读取、池参数、特殊字符密码、真实 SQLAlchemy SQLite SELECT 1、连接上下文释放、错误分类与日志保护、Session 独立/回滚/关闭/不自动提交、健康接口成功失败、初始化和释放异常。
- SQLite 仅用于验证 SQLAlchemy SQL 和资源行为，Mock 仅用于受控失败路径；均不代表真实 MySQL 集成成功。
- 中间曾有 1 个旧路由集合断言失败，更新集合以精确覆盖新增接口后已通过；中间格式检查发现 CRLF 需规范化，最终通过。

## 7. 真实数据库验证及未执行内容

已运行独立集成检查，结果 REAL_MYSQL_RESULT=database_not_configured，退出码 2。统一配置没有同时提供有效 MYSQL_USER 和 MYSQL_DATABASE，故未尝试网络连接；没有编造连接成功。独立预检的 finally 已确认 POOL_CLOSED=True；集成检查的 TestClient 上下文也会退出并关闭资源。

由于连接配置不完整，真实 MySQL SELECT 1、真实 MySQL Session 操作及真实数据库健康接口成功路径尚未执行。真实环境认证、网络可达性、数据库权限和驱动认证插件兼容性尚未得到验证。未创建、清空或修改任何业务表；未开发迁移、模型、CRUD 或其他下一阶段功能。

## 8. 遗留问题与人工验收

由用户在本地统一配置中安全提供 MYSQL_USER、MYSQL_DATABASE 以及适用的主机、端口、密码后，重新运行独立集成检查。不得把真实密码提交到仓库。预期退出码 0 且输出 REAL_MYSQL_RESULT=SELECT_1_SESSION_HEALTH_LIFECYCLE_OK，再确认实际部署的 /api/v1/health/db 返回 200、数据库不可用时返回 503 且存活接口仍返回 200。

最终验收结论：**部分完成**。自动化设施验收通过，真实 MySQL 验收待完成。本次停止，等待用户审核，不进入 P6-BASE-007。

---

## 9. 补充真实 MySQL 集成验收（2026-11-04 16:19，Asia/Shanghai）

**最新最终状态：已完成。** 本节为追加记录，保留前述历史结果；第 7、8 节的配置阻塞和“部分完成”状态已由本次真实验收解除。

### 9.1 环境与配置来源

- 项目工作目录：D:\AI\DigiTalent_AI。
- Conda 环境：feiyu；使用 Conda PowerShell hook 后激活，复核通过。
- Python：3.11.18。
- 解释器：D:\anaconda3\envs\feiyu\python.exe。
- pip：26.2.2，D:\anaconda3\envs\feiyu\Lib\site-packages\pip。
- pytest 可执行文件：D:\anaconda3\envs\feiyu\Scripts\pytest.exe。
- Settings.model_config.env_file 正确指向项目根目录 .env，文件存在；工作目录与项目根目录一致。
- 使用现有 get_settings() 加载，不绕过统一配置机制；通过 Pydantic DotEnvSettingsSource 在内存中核对配置来源，读取到 10 个 MySQL 配置字段。
- 没有 MySQL 进程环境变量覆盖；统一加载结果与配置来源一致，MYSQL_USER 和 MYSQL_DATABASE 均已配置。
- 检查仅输出路径检查、字段数量、布尔值及固定状态；未输出 .env 内容、实际配置值、密码或完整 DSN，未修改用户配置。

### 9.2 执行命令

```powershell
conda env list
(& conda 'shell.powershell' 'hook') | Out-String | Invoke-Expression
conda activate feiyu
python --version
python -c "import sys; print(sys.executable)"
python -m pip --version
Get-Command pytest

# 复核环境后，明确使用该解释器执行：
& 'D:\anaconda3\envs\feiyu\python.exe' -m tests.mysql_integration_check
& 'D:\anaconda3\envs\feiyu\python.exe' -m ruff check app tests
& 'D:\anaconda3\envs\feiyu\python.exe' -m ruff format --check app tests
& 'D:\anaconda3\envs\feiyu\python.exe' -m pytest -q
```

此外通过 PowerShell here-string 管道传给同一个 feiyu Python 解释器，执行了只读来源核对和补充生命周期/失败检查。脚本仅在内存中使用 TestClient、SQLAlchemy 事件、unittest.mock.patch，不修改任何项目代码或数据库配置。

### 9.3 真实数据库与 Session 验证

现有独立集成命令退出码 **0**，输出：

```text
REAL_MYSQL_RESULT=SELECT_1_SESSION_HEALTH_LIFECYCLE_OK
```

- 真实 MySQL 连接成功，Database.check() 的 SELECT 1 成功。
- 通过真实 get_session 依赖创建 SQLAlchemy Session，Session 执行 SELECT 1 返回 1。
- 补充检查通过 spy 确认 Session.close() 调用一次；依赖结束后 checkedout() 从 1 回到 0。
- 健康检查后连接池 checkedout() 为 0，连接已归还。
- 应用关闭后 database.closed 为 True；SQLAlchemy Engine 的 close 事件确认真实 DBAPI 物理连接已关闭，原连接池 checkedout() 为 0。
- 关闭后再次调用 close() 不会重复调用 Engine.dispose()，幂等关闭通过。

### 9.4 健康检查、受控失败及脱敏

使用 TestClient 调用现有应用路由，正常路径使用真实 MySQL；失败路径仅临时 patch 当前 Engine.connect，使其抛出带合成敏感标记的 OperationalError（驱动错误码 2003），不停止或破坏真实数据库服务。

| 验证项 | 结果 |
| --- | --- |
| /api/v1/health/db 连接真实 MySQL | 200，通过 |
| 受控连接失败 /api/v1/health/db | 503，reason=connection_failed，通过 |
| 同一失败期间 /api/v1/health | 200，通过 |
| 失败诊断日志 | 仅输出固定 connection_failed 分类，通过 |
| 成功、失败及存活响应和采集日志脱敏 | 不含实际密码、合成敏感标记或 MySQL DSN 前缀，通过 |
| patch 退出后重新检查真实数据库 | 200，通过 |
| 失败与恢复后的连接池 | checkedout()=0，通过 |

失败路径是受控测试，真实连接、SQL、Session 和成功健康路径使用实际 MySQL，二者结果明确区分。HTTP 验证使用应用内 TestClient，没有另起 Uvicorn 或验证外部反向代理部署。

### 9.5 回归、变更范围与结论

- Ruff：All checks passed。
- Ruff 格式检查：25 files already formatted。
- pytest：**97 passed，0 failed，0 skipped，0.65 秒**。
- 独立真实 MySQL 集成检查：通过，退出码 0。
- 补充来源、资源、受控失败及脱敏断言全部通过；这些为独立检查，不计入 pytest 97 项。
- 本次仅向本报告追加验收记录；未修改应用、测试代码和用户 .env；未安装、升级或替换依赖，未提交 Git Commit。
- 数据库仅执行 SELECT 1 及驱动连接初始化/事务清理，不创建或修改业务表和业务数据。
- 未解决问题：本任务验收范围内无。

**P6-BASE-006 最终验收结论：已完成。** 停止本次工作，等待用户审核，不进入 P6-BASE-007。
