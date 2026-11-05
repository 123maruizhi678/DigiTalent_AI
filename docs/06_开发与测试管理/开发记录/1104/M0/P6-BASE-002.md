# P6-BASE-002：建立统一配置加载机制

- 日期：2026-11-04（Asia/Shanghai）
- 当前状态：开发与技术验证完成，达到当前任务验收标准，等待用户审核。
- 依据：用户指定的 M0 实施方案、P6-BASE-001.md、P6-FE-001.md、根目录 AGENTS.md。
- 后端实际目录：项目根目录 app/，沿用已验收布局，不创建或迁移到 backend/。

## 1. 首次检查与实施计划

首次检查 app/、tests/ 相关代码及根目录依赖、忽略规则，确认：

- main.py 创建应用、保留 lifespan 并挂载总路由；标题 DigiTalent AI 和版本前缀 /api/v1 原先分别在 main.py、router.py 硬编码。
- core/ 仅有包声明，无 Settings 或其他配置机制；后端及测试未发现 os.getenv/environ 读取。
- .env、.env.example、本报告首次均不存在；未读取真实 .env 内容，未创建真实 .env。
- feiyu 环境 Pydantic 2.14.2、pydantic-settings 2.16.2 已安装且 requirements.txt 已精确声明；不需要新依赖。
- Git 存在原有暂存 requirements.txt、未跟踪后端交付及其他既有前端状态。保留索引和工作区，不回退、不替换。
- 根 AGENTS.md 现有附加规范要求中文配置说明：已逐字段使用中文 Field(description)，提供类型、默认、范围、必填性与敏感性说明，并同步模板。
- “已确认后端架构”未提供准确文档路径，未搜索或读取替代文档；按指定 M0 中已明确的 core 配置职责及现有分层实施。

实施前已向用户说明计划：新增统一配置、环境模板和测试；增量修改入口、路由前缀挂载位置及忽略规则。采用默认值即可启动，不要求未来服务凭据；日志仅定义最小配置项，不提前实现 BASE-003。

## 2. 实际新增文件

| 文件 | 职责与内容 |
| --- | --- |
| app/core/config.py | Settings、字段中文说明和校验、安全错误类型、缓存单例；项目根 .env 路径固定，不初始化服务 |
| .env.example | 8 个实际配置项的中文用途、类型、默认、范围、必填和敏感性说明；外部服务分类预留 |
| tests/unit/test_config.py | 31 个实际参数化配置测试，临时环境及临时 .env 隔离，不修改真实配置 |
| docs/开发日记/1103/P6-BASE-002.md | 本阶段首次检查、执行和验收记录 |

## 3. 实际修改文件

| 文件 | 具体增量修改 |
| --- | --- |
| app/main.py | 导入并调用 get_settings；标题和 debug 读取统一配置，include_router 使用配置前缀；保留原版本信息和完整 lifespan；增加 python -m app.main 启动路径，使用配置 HOST/PORT |
| app/api/router.py | 将固定前缀从聚合器移至 main.py 挂载处，路由聚合及健康路由注册保持原样，避免重复前缀 |
| .gitignore | 追加 .env、.env.* 忽略规则，保留 !.env.example；原有规则不变 |

未修改：健康路由代码、原有健康测试、任何前端文件、Element Plus 实现、依赖文件、AGENTS.md、三份依据报告或 M0 方案。未删除、重命名、迁移或重新生成已有入口；未操作 Git 索引。

## 4. 配置项清单

以下全部非敏感、非必填（省略使用默认值）；提供值后须满足约束。名称与环境模板完全一致。

| 名称 | 中文名称及用途 | 类型 | 默认值 | 合法范围 |
| --- | --- | --- | --- | --- |
| APP_NAME | 应用名称，FastAPI 标题 | str | DigiTalent AI | 去除两端空白后非空 |
| APP_ENV | 运行环境标识 | Literal 字符串 | development | development/test/production |
| DEBUG | FastAPI 调试模式 | bool | false | Pydantic 布尔解析 true/false、1/0、yes/no、on/off 等 |
| API_V1_PREFIX | 总 API 版本前缀 | str | /api/v1 | / 开头，非空路径段，字母数字下划线连字符，不允许尾斜杠 |
| HOST | 内置模块启动监听地址 | str | 127.0.0.1 | 去除两端空白后非空；应提供有效主机名或 IP，实际绑定由服务器处理 |
| PORT | 内置模块启动监听端口 | int | 8080 | 1～65535 |
| LOG_LEVEL | 后续日志设施的统一级别 | Literal 字符串 | INFO | DEBUG/INFO/WARNING/ERROR/CRITICAL，输入转大写 |
| LOG_OUTPUT | 后续日志输出方式 | Literal 字符串 | console | 仅 console，不主动写入受限目录 |

环境枚举在既有 M0 中未明确列出具体取值，本轮限定 development/test/production 并在定义、模板、测试和报告统一，不建立其他环境机制。

MySQL、Milvus、Ollama、MinerU、文件存储、模型服务、任务调度仅有中文分类预留，不虚构连接参数、真实凭据或客户端。未来敏感字段要求使用 SecretStr、repr=False 及中文说明，首次使用时再定义与测试。

## 5. 加载机制与入口行为

- Pydantic Settings 读取进程环境变量及项目根 .env，生产调用仅 get_settings()，不传构造参数。
- 运行时优先级：进程环境变量 > 项目 .env > 代码默认值。测试显式传入字段值时遵循 Settings 原生“构造参数优先”的语义，用于隔离测试。未配置文件 secrets 目录。
- .env 路径通过 config.py 所在位置推导为项目根绝对路径，不依赖当前工作目录；UTF-8 读取。
- extra=ignore 允许未来共享 .env 中未建模字段存在，但不将这些字段加入配置对象；不意味着已经支持这些服务。
- @lru_cache(maxsize=1) 集中创建单例，frozen=True 防止创建后被修改。进程内配置固定；调整环境后应重启服务。cache_clear 只用于隔离测试。
- 没有在业务模块加入 os.getenv 或重复 Settings 实例。
- 原有启动命令仍可用；Uvicorn 命令行显式 --host/--port 由 Uvicorn 决定，不能声称环境变量会改写命令行参数。
- 新增下列启动方式直接使用 Settings.HOST/PORT；既有 lifespan 和路由组装沿用：

```powershell
# 在 D:\AI\DigiTalent_AI 执行
& 'D:\anaconda3\envs\feiyu\python.exe' -m app.main
# 原启动方式仍可用；此方式地址和端口来自命令行
& 'D:\anaconda3\envs\feiyu\python.exe' -m uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload
```

LOG_LEVEL、LOG_OUTPUT 此阶段负责加载与校验，留给 BASE-003 消费，不新增日志初始化或异常中间件。DEBUG 仍默认关闭。

## 6. 配置合法性与安全验证

- 合法端口 1/8080/65535；非法端口 0/65536/-1/非数字/小数均有测试。
- DEBUG 测试 true/false、1/0、yes/off，非法 maybe 被拒绝。
- 非法环境、日志级别、API 路径、空名称/地址、非法输出方式均被拒绝。
- 所有当前字段有默认值，不引入无默认值的 M0 部署门槛；名称、地址提供空值仍校验失败。另用临时 RequiredSettings 子类验证未来必需字段缺失会指出 APP_NAME 和 Field required，不把此测试子类当作生产必填配置。
- hide_input_in_errors=True 隐藏直接 ValidationError 的字符串输入，字段 repr=False 防止普通配置 repr 输出值。
- 生产 get_settings 将 ValidationError 转换成仅列出配置字段名的 ConfigurationError；配置源错误仅输出通用来源说明，raise from None 避免正常 traceback 输出原始异常上下文。没有打印配置字典或环境内容。
- 仅使用人工假值验证脱敏；实际启动子进程 PORT 为假敏感字符串时非零退出，stderr 包含 PORT 而不包含该假值。
- 临时 .env 中的未知假 MYSQL_PASSWORD 不进入配置对象及 repr，未定义或读取未来服务凭据。
- 不将 Pydantic 原始 errors()/model_dump() 作为日志脱敏接口；当前没有敏感字段，后续新增仍必须单独保护和测试。

## 7. Git 配置保护检查

实际命令：

```powershell
git check-ignore --no-index .env .env.local
git check-ignore --no-index .env.example
git ls-files -- .env '.env.*' 'app/**/.env' 'app/**/.env.*'
```

结果：.env、.env.local 被忽略；.env.example 的 check-ignore 退出 1（没有被忽略，符合预期）；限定后端范围的已跟踪环境文件查询为空。没有擅自取消跟踪或删除文件。真实 .env 始终不存在，未写入模板。此检查不等同于扫描整个仓库进行历史凭据审计。

## 8. 实际执行命令与测试证据

首次检查包括：Get-Content AGENTS.md、当前入口/聚合器/健康路由/.gitignore；rg --files --hidden app tests；rg 检查配置读取及依赖声明；feiyu Python importlib.metadata 检查安装版本；Test-Path 检查环境模板和报告；git status --short --untracked-files=all 与 git diff --cached --stat 检查任务相关路径；精确读取三份授权依据及 M0 任务三段落，未扫描文档目录。

通过 apply_patch 增量实现第 2～3 节文件，执行：

```powershell
& 'D:\anaconda3\envs\feiyu\python.exe' -m pytest tests -q -p no:cacheprovider
```

结果：33 passed in 0.38s，退出码 0，包括配置相关 31 项与原有 API 回归 2 项。未覆盖或创建测试结果文件。独立测试通过 monkeypatch 清除本测试涉及的配置变量、禁用真实 .env，dotenv 只使用 tmp_path 文件。结束清理单例并恢复环境，不影响真实配置。

实际配置覆盖测试验证 APP_NAME、APP_ENV、DEBUG、API_V1_PREFIX、HOST、PORT、LOG_LEVEL；临时 dotenv 提供名称和端口，进程环境覆盖其中端口。模板读取测试验证 8 项默认值一致且所有字段提供中文说明。替换前缀的 FastAPI 集成测试验证 /api/test/health 可用、旧路径不重复注册，并在 finally 恢复默认应用配置。

额外执行 feiyu Python 内存验证脚本：

1. socket.bind 确认约定 8080、5173 可用。
2. subprocess 启动 python -m app.main；GET /api/v1/health 返回 HTTP 200 与 {"status":"ok","service":"digitalent-ai"}。
3. GET /openapi.json 标题为默认 DigiTalent AI。
4. 启动现有 Vite 入口，GET http://127.0.0.1:5173/api/v1/health 经代理返回同一 HTTP 200 JSON。
5. CTRL_BREAK_EVENT 关闭仅本轮启动的进程 PID 31968、22716。后端日志确认 Application startup complete、Application shutdown complete 和进程退出。
6. 独立子进程以非法假 PORT 导入应用，非零退出且不输出假敏感值。
7. TCP 检查 8080、5173、18080 均无服务接受连接，验证脚本退出 0。

git diff --check -- app/main.py app/api/router.py .gitignore 退出 0；因后端交付尚未被用户提交、原有文件仍未跟踪，另用实施前的 SHA-256 快照比较原有源码，确认仅 main.py 和 router.py 内容变更，原有 tests、frontend/src、前端依赖与锁文件、requirements.txt、AGENTS.md 均保持原样。新增文件按补丁与测试检查，不以空 Git diff 代替未跟踪文件审查。

未重新运行前端全量构建与组件测试：前端代码和依赖无变更，实际前端代理已回归；沿用上一任务已有构建及 23 项测试证据，不将它们表述为本轮重新执行。

## 9. 依赖变化与遗留问题

依赖变化：无。使用已有 feiyu 环境和已声明的 pydantic-settings 2.16.2/Pydantic 2.14.2，没有安装、升级或修改 requirements.txt。

未发现本任务功能阻塞。未来外部服务凭据、日志基础设施、数据库连接和安全模块尚未实施，属于后续任务，不作为本阶段缺陷。后端架构独立文档未提供准确路径，本轮没有扩大文档读取范围；可依据当前代码和指定 M0 规则审核此次变更。

## 10. 验收结论与下一项

统一配置、默认值/来源覆盖/合法性、中文字段及模板、脱敏错误、单例与不可变性、Git 忽略、现有生命周期、健康接口和前端代理回归均通过，达到 P6-BASE-002 技术验收标准，等待用户审核。

下一项为 P6-BASE-003：日志与异常基础设施。本轮未开始该任务，也未修改其他已验收前端成果。完成汇报后停止，等待用户确认。
