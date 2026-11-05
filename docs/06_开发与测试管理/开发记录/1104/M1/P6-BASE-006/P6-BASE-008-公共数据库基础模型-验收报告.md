# P6-BASE-008 公共数据库基础模型验收报告

日期：2026-11-04（Asia/Shanghai）

最终状态：**已完成**。公共基础代码、隔离验证、121 项自动化回归及真实 MySQL 集成验收均已通过。原阶段记录保留如下，最新验收结论见第 12 节。

## 1. 范围与原有实现检查

- 已检查根目录 AGENTS.md、app/core/config.py、database.py、migrations.py、migrations/env.py、测试和 requirements。
- 原代码无 DeclarativeBase、公共 ORM UUID、时间或状态实现；middleware 的 UUID 用于请求标识，不承担 ORM 主键职责。
- 原 migrations.get_target_metadata() 返回 None；迁移入口已有在线、离线、外部连接注入、安全错误诊断和资源释放逻辑，均保留。
- Database 统一管理同步 Engine 和 sessionmaker，get_session 管理请求 Session、异常回滚和关闭；本次未改动。
- 依赖锁定并实际安装：SQLAlchemy 2.1.6、Alembic 1.20.1。未安装、升级或修改依赖。
- 原有 revision 为 20261104_0001，down_revision=None，空结构基线；保持完整。
- 工作区原有大量已修改及未跟踪文件；本次保留这些工作，不提交 Git Commit。
- 未扫描或读取 docs 内容；仅按任务末尾指定范围新增本报告。

## 2. 文件交付

以下路径均相对于 D:\AI\DigiTalent_AI；“新增/修改”指本次操作，部分原有文件此前已处于未跟踪状态。

| 操作 | 文件 | 职责 |
| --- | --- | --- |
| 新增 | app/core/orm.py | 唯一 Base、metadata 与约束命名规范 |
| 新增 | app/core/model_mixins.py | UUID、UTC 时间类型和时间字段、公共记录状态及独立 Mixin |
| 新增 | app/models/__init__.py | 正式模型显式注册入口，当前没有业务实体 |
| 新增 | tests/unit/test_orm.py | 测试专用模型、ORM 往返、状态约束、DDL 和迁移生成验证 |
| 修改 | app/core/migrations.py | 注册正式模型后返回 Base.metadata，保留原迁移流程 |
| 修改 | migrations/env.py | 更新 metadata 接入说明，入口仍只调用统一迁移模块 |
| 修改 | tests/unit/test_migrations.py | 将原 None 契约更新为唯一 metadata；验证空 metadata 可通过 Alembic check |
| 新增 | docs/开发日记/1104/P6-BASE-008-公共数据库基础模型-验收报告.md | 本次验收记录 |

未修改配置、依赖、数据库连接实现和基线迁移；未创建用户、组织、角色、人才、Agent 或 Workflow 实体。

## 3. UUID 规范与方案比较

采用 SQLAlchemy Uuid(as_uuid=True, native_uuid=False)，Python 类型统一为 uuid.UUID，写入时通过 uuid4 自动生成；所有数据库存储为 CHAR(32) 小写十六进制，API 通过 Pydantic UUID 字段、FastAPI jsonable_encoder 或 str(uuid) 输出标准带连字符字符串。

| 方案 | 存储与索引 | 可读性与兼容性 |
| --- | --- | --- |
| CHAR(36) | 36 个字符，比 CHAR(32) 多四个分隔符；实际字节受字符集影响 | 标准展示直接可读，但需额外统一转换 |
| BINARY(16) | 紧凑的 16 字节键，索引更小 | SQL 手动检查不直观，需要二进制转换规则 |
| SQLAlchemy Uuid，禁用 native_uuid | 统一 CHAR(32)，索引比二进制键大 | 内置 UUID 绑定及读取转换，跨 MySQL/SQLite 规则一致 |

选择第三种以复用现有依赖的类型转换并保持跨数据库一致；不以本次隔离测试推断 MySQL 索引性能。随机 UUID4 不提供顺序写入优化。未来 UUID 外键必须采用相同 Uuid 参数，不混用 CHAR(36) 或 BINARY(16)。

默认 UUID 在 INSERT/flush 时生成，不承诺对象构造完成即已有主键；Python 标准 json.dumps 不直接支持 UUID，应使用上述序列化入口。

## 4. 时间规范

- created_at、updated_at 均非空，创建时由统一 utc_now 自动填充。
- Python 使用带 UTC 时区 datetime；拒绝无时区输入，其他时区输入先转换到 UTC。
- 数据库保存去掉 tzinfo 的 UTC 值；读取恢复 UTC 时区，不依赖 MySQL 会话时区。
- MySQL 类型 DATETIME(6)，六位小数微秒精度；SQLite 用 DateTime 验证往返语义。
- updated_at 使用统一 SQLAlchemy onupdate，覆盖 ORM 与 SQLAlchemy Core 普通更新；created_at 无 onupdate，普通更新保持原值。
- 原始 SQL 和其他数据库客户端不会自动执行客户端默认值/onupdate，必须显式提供 UUID、UTC 创建/更新时间。本次未引入触发器或数据库 ON UPDATE CURRENT_TIMESTAMP。
- created_at 可显式修正，本次没有将其实现为不可变字段；无实际更新的 flush 不刷新时间。

## 5. 公共状态规范

- 按需继承 RecordStatusMixin，字段名 status，非空，默认 RecordStatus.ACTIVE。
- RecordStatus 为 StrEnum，只含 active（可用）与 inactive（停用）。
- 数据库存储 VARCHAR(8)，带命名 CHECK 约束；同时有服务端默认值 active。
- Python 绑定只接受 RecordStatus；原始字符串、整数及其他业务枚举即使值为 active 也被拒绝，防止误混用。
- 此字段仅表达公共记录可用性，不表达用户账号、任务执行或审批状态；这些业务含义须在后续模块中独立定义，不要求继承此 Mixin。
- CHECK 的真实 MySQL 执行效果尚待在线验证，特别是旧 MySQL 版本对 CHECK 的支持差异；DDL 编译不等同于服务端约束生效。

## 6. Mixin 使用与模型注册

Base 不强制注入任何字段。新实体默认按 UUIDPrimaryKeyMixin + Base 组合；时间及公共记录状态按需加入 TimestampMixin、RecordStatusMixin。特殊主键模型可以只继承 Base 并声明所需字段。

生产唯一继承入口为 app.core.orm.Base，唯一 metadata 为 Base.metadata；业务模块不得自行声明 Base 或 metadata。测试模型均位于 tests/unit/test_orm.py，通过继承公共 Base 验证独立及组合字段；测试专用 mapper 生命周期隔离，结束移除测试表，正式注册入口不导入测试。

app.models.register_models() 是唯一正式模型注册入口，当前不包含实体；后续公共实体、IAM、人才档案、Agent 和 Workflow 模型应在此显式导入。迁移入口先调用 register_models，再返回 Base.metadata，不扫描目录、不吞掉导入异常。

## 7. Alembic 与结构验证

- 原基线 revision 关系、在线/离线迁移和连接释放测试继续通过。
- 空正式 metadata 执行 Alembic command.check 成功，无结构变化，不生成无意义 revision。
- SQLite 内存隔离库通过 compare_metadata 发现四个测试表；produce_migrations 生成操作，render_python_code 验证创建表迁移文本；通过 Alembic Operations 实际执行后再次比较得到空差异。
- 未使用 Base.metadata.create_all 替代迁移；未在正式 versions 目录生成测试 revision，原正式目录仍只有原有空基线。
- MySQL 方言编译断言包含 CHAR(32)、两个 DATETIME(6)、VARCHAR(8)、CHECK 和主键；这仅是类型及 SQL 编译验证。
- 所有后续自动生成迁移须人工审核，特别防止未注册模型或空 metadata 对现有库生成删除操作；本次未连接现有数据库。

## 8. Python 环境与执行结果

- Conda：feiyu。
- Python：3.11.18。
- 解释器：D:\anaconda3\envs\feiyu\python.exe。
- pip：26.2.2，D:\anaconda3\envs\feiyu\Lib\site-packages\pip。
- 已执行 conda env list、conda run -n feiyu python --version、conda run -n feiyu python -c "import sys; print(sys.executable)"、conda run -n feiyu python -m pip --version，均符合要求。

最终测试命令：

```powershell
$env:PYTHONIOENCODING='utf-8'
conda run --no-capture-output -n feiyu python -m pytest -q
conda run --no-capture-output -n feiyu python -m ruff check app/core/orm.py app/core/model_mixins.py app/models app/core/migrations.py migrations/env.py tests/unit/test_orm.py tests/unit/test_migrations.py
conda run --no-capture-output -n feiyu python -m ruff format --check app/core/orm.py app/core/model_mixins.py app/models app/core/migrations.py migrations/env.py tests/unit/test_orm.py tests/unit/test_migrations.py
git diff --check
```

最终结果：**121 passed，0 failed，0 skipped**，耗时 1.38 秒；包含新增 ORM 测试 13 项、迁移测试 11 项以及数据库、配置、API 等既有回归。Ruff 检查通过，7 个文件格式符合要求；Git 差异检查通过，仅提示原有工作区文件换行转换信息。

过程记录：首轮相关测试 23 项通过。补充测试后一次全量运行出现测试作用域 NameError（test_orm.py 的独立 Mixin 用例）及 mapper 清理警告，均修正后重跑通过，未删除原有测试或降低断言。一次 Conda 捕获 Ruff 输出时出现 GBK 编码错误，改用当前进程 UTF-8 输出和 --no-capture-output 解决；未修改 Conda 环境配置，所有 Python 操作始终使用 feiyu。

## 9. 未执行项、遗留问题与人工验收

1. 未执行真实 MySQL 在线迁移、索引、字段精度往返及数据库约束测试：当前没有确认可用的隔离 MySQL 测试库，不使用现有业务库替代。
2. BASE-007 的真实 MySQL 在线迁移验证继续保留为待办，不标记完成。
3. 后续需在明确的隔离 MySQL 库验证 UUID/外键、DATETIME(6) 往返、状态 CHECK 和 Alembic 在线迁移行为，并检查实际结构及版本记录；目前没有 MySQL DDL 失败需要恢复的情况。
4. 人工审查 UUID CHAR(32)、客户端时间默认值及可用性状态语义是否符合后续业务模型使用要求；本次未读取受限设计文档来推断其中约定。

## 10. 验收结论

代码与隔离验收已完成：唯一 Base、UUID 类型与生成、UTC 时间、公共状态、独立/组合 Mixin、正式模型注册入口、Alembic metadata 接入均通过自动化验证；未破坏 BASE-006/007 的回归用例，未新增业务表、未修改依赖、未操作真实数据库或业务数据。

整体状态保守记录为“部分完成”，剩余为真实隔离 MySQL 在线验收。此次交付后停止，不进入 P6-IAM-001 或 P6-BASE-009。

## 11. 补充真实 MySQL 集成验收：环境预检（2026-11-04）

本轮状态：**阻塞，等待隔离测试库授权**。整体任务仍为部分完成；以上 121 项自动化测试记录原样保留，本轮未重新执行或将其计作 MySQL 测试。

### 环境与只读连接结果

- 使用 Conda feiyu，Python 3.11.18。
- 解释器：D:\anaconda3\envs\feiyu\python.exe。
- pip 26.2.2，路径 D:\anaconda3\envs\feiyu\Lib\site-packages\pip。
- 执行 conda env list、conda run -n feiyu python --version、conda run -n feiyu python -c "import sys; print(sys.executable)"、conda run -n feiyu python -m pip --version；均符合要求，退出码为 0。
- 通过项目 get_settings() 读取统一连接配置，复用 Database 创建连接；未直接打印 .env、密码或完整 URL。
- 只读预检通过 PowerShell here-string 管道交给 conda run --no-capture-output -n feiyu python - 执行，退出码为 0。
- MySQL 主机为 127.0.0.1，端口 3306；当前配置数据库为 agent_service，账号和密码已配置。
- 实际执行 SELECT VERSION(), DATABASE()，确认版本 **8.0.44**、当前数据库 agent_service，真实在线连接成功。
- 仅通过 information_schema.SCHEMATA 对候选名称 digitaltalent_base008_test 作精确查询，当前账号未看到该库。此结果不证明服务器上绝对不存在该库，也不代表账号具备创建库权限。
- agent_service 未被用户确认为可执行破坏性测试的隔离库，本轮没有在其中建表、写入、迁移或回滚。

### 验收项目状态

| 项目 | 本轮真实 MySQL 结果 |
| --- | --- |
| MySQL 版本和在线连接 | 已验证：8.0.44，只读连接成功 |
| 测试数据库性质 | 尚无确认并授权的专用隔离测试库 |
| UUID 自动生成、存储类型、往返、唯一性、外键 | 未执行，等待隔离库 |
| created_at / updated_at、DATETIME(6)、微秒、UTC、时区转换 | 未执行，等待隔离库 |
| active 默认值、inactive 写入、非法状态拒绝 | 未执行，等待隔离库 |
| CHECK 真实生效 | 未执行；已取得实际 MySQL 版本，但不能据此宣称约束验收通过 |
| Alembic 版本读取、upgrade / downgrade / 再次 upgrade | 未执行，避免触碰未授权的现有数据库迁移状态 |
| alembic_version 与模型结构一致性 | 未执行，等待隔离库 |

### 所需数据库与权限

建议专用隔离库名称：digitaltalent_base008_test，位于上述本地实例，明确仅用于 P6-BASE-008 集成验收，不承载业务数据。

由管理员提供已存在的空隔离库，或由用户明确授权创建该库。若授权由本任务创建，只需对这个指定数据库进行 CREATE DATABASE；不需要全局 DROP DATABASE 权限，本任务不请求删除数据库。

测试账号在该隔离库内需要 SELECT、INSERT、UPDATE、DELETE、CREATE、ALTER、DROP、INDEX、REFERENCES 权限；DROP 仅用于本轮测试表及隔离库内 Alembic 版本表的迁移回退，不涉及现有业务库。账号授权与凭据由用户或管理员提供，不在报告中记录密码。

本轮只修改此验收报告，未改公共模型、配置、依赖或测试代码；未创建/删除数据库，未执行任何 DDL/DML，未提交 Git。BASE-007 在线迁移验证继续保留为待办。下一步等待用户确认隔离库及其使用授权，再执行本轮指定的真实集成验收。

## 12. 用户授权后的真实 MySQL 集成验收（2026-11-04）

最终状态：**已完成**。用户回复“授权给你”后，按第 11 节明确提出的数据库名称与权限范围执行；本节结果取代此前“待授权、MySQL 未执行”的当前状态，历史测试记录保持不变。

### 12.1 本轮范围、文件职责与前置检查

- 本轮仅补充 P6-BASE-008 真实 MySQL 验收，不重新开发公共模型，不开展其他业务任务。
- 再次检查并复用 app.core.model_mixins、Base、Database、统一 Settings、迁移入口及 20261104_0001 基线。
- BASE-006 连接与 Session 实现可用；BASE-007 原在线迁移入口被实际调用；BASE-008 公共模型在真实 MySQL 上验证。
- 新增 tests/mysql_base008_integration_check.py：显式手工运行的真实 MySQL 验收脚本，不被 pytest 自动收集，不导入生产模型注册入口。测试模型仅在脚本运行时定义。
- 修改本验收报告：追加真实结果并更新顶端最终状态，保留原有 121 项测试及预检记录。
- 未修改公共模型、迁移框架、正式 revisions、共享配置、.env、依赖及原有测试。无依赖安装或升级；已有用户工作区改动保留，未提交 Git。

### 12.2 环境、数据库性质与安全边界

- Conda feiyu，Python 3.11.18；解释器 D:\anaconda3\envs\feiyu\python.exe；pip 26.2.2 来自 D:\anaconda3\envs\feiyu\Lib\site-packages\pip，执行前复核通过。
- MySQL 实际版本 **8.0.44**，本地实例 127.0.0.1:3306。
- 经授权创建专用库 **digitaltalent_base008_test**，首次确认库内没有表；不承载业务数据。
- 使用项目 get_settings()，仅在内存中通过 model_copy 覆盖 MYSQL_DATABASE 为专用库，复用 Database；没有修改 .env、打印密码或完整连接字符串。
- 脚本必须显式提供 --allow-isolated-ddl；目标库名称固定。拒绝带视图、现有实体表或非空迁移版本的库。允许再次运行时仅存在无版本记录的 alembic_version 表。
- 原 agent_service 仅用于读取现有连接配置及发出经授权的指定库创建语句；未改其表、数据或迁移版本，未执行该库的 upgrade/downgrade。
- 所有测试表迁移脚本生成在 TemporaryDirectory 中，正式 migrations/versions 仍保持原空基线。

### 12.3 UUID 真实结果

**通过。** 每轮插入 100 个模型对象，自动生成 100 个不同 UUID4；Python 类型均为 uuid.UUID。

- MySQL 反射实际主键为 CHAR(32)，原生 SQL 读取与 UUID.hex 相等。
- 按 UUID 主键查询可往返还原；子表引用父表 UUID 后可正确读取。
- 父主键与子外键存储均为 CHAR(32)，实际外键存在。
- 绕过 ORM 插入不存在的父 UUID，被 MySQL 拒绝，错误码 **1452**，确认外键实际生效。

### 12.4 时间字段真实结果

**通过。** 反射取得两个 DATETIME 字段，information_schema.COLUMNS 显示 created_at、updated_at 的 DATETIME_PRECISION 均为 **6**，即 DATETIME(6)。

- 创建时 created_at、updated_at 自动填充，读取后带 UTC 时区。
- 普通 ORM 更新自动刷新 updated_at，created_at 保留原值。
- SQLAlchemy Core update 同样自动刷新 updated_at。
- 显式写入 2026-11-04 12:30:00.123456 +08:00，读取为等值 UTC 时间 2026-11-04 04:30:00.123456 +00:00，微秒 123456 保留。
- 原始 SQL 读取为无时区 UTC 2026-11-04 04:30:00.123456，符合公共存储约定。
- 实际设置会话 time_zone='+08:00' 后写入约定的无时区 UTC 值，ORM 读取仍还原等值 UTC；DATETIME 不发生额外会话时区偏移。
- 客户端默认值与 onupdate 的边界不变：直接原始 SQL 须显式提供 UUID 和时间字段，本次没有新增触发器或服务端时间填充规则。

### 12.5 公共状态与 CHECK 真实结果

**通过。** 实际状态列为 VARCHAR(8)。

- ORM 默认返回 RecordStatus.ACTIVE；更新为 INACTIVE 后往返返回同一枚举值。
- 非法 Python 状态被绑定校验拒绝，Session 回滚后继续执行后续验证。
- 原始 SQL INSERT 省略 status 时，MySQL 服务端填入 active。
- 实际约束名称 ck_base008_test_parent_record_status，information_schema.TABLE_CONSTRAINTS 显示 **ENFORCED=YES**。
- 绕过 Python 校验，以原始 SQL 将 status 更新为 invalid，被 MySQL CHECK 拒绝，错误码 **3819**。
- 因此本地 MySQL 8.0.44 对本次 CHECK 约束支持并实际执行；不是仅凭版本或 SQLite 结果推断。

### 12.6 Alembic 在线迁移与结构结果

**通过。** 在真实专用 MySQL 库中使用原 migrations/env.py 和统一迁移入口；连接由复用的 Database 提供，通过已有外部连接注入机制传递。

1. 原框架基线 upgrade 至 20261104_0001，读取 alembic_version 正确。
2. 通过真实库的 MigrationContext 和公共 Base.metadata 执行 produce_migrations，发现两个测试表。
3. 将 upgrade/downgrade 操作渲染成临时 revision base008_mysql_test，down_revision 为 20261104_0001。渲染时显式处理 UTCDateTime、RecordStatusType 的构造表达式，临时迁移引用公共类型；没有修改生产迁移的渲染机制。
4. upgrade head 成功，alembic_version 为 base008_mysql_test；command.current 输出包含该版本。
5. compare_metadata(compare_type=True) 返回空差异，另以真实字段精度及 CHECK、外键检查补充比对。
6. downgrade base 成功，移除两个测试表，版本记录为空。
7. 再次 upgrade head 成功，版本恢复为 base008_mysql_test，模型结构比较再次为空差异。
8. 最终再次 downgrade base 清理本轮测试实体和样本数据，仅保留空的 alembic_version 表及专用数据库；**没有删除数据库**。

测试 revision 只存在临时目录，退出后自动移除；正式迁移目录没有测试表或测试 revision。未使用 metadata.create_all 替代 Alembic。

本轮未发生 MySQL DDL 失败。脚本失败路径会只读检查实际表清单及版本，不以“事务回滚”推断 DDL 已完整恢复，也不自动删除异常残留表。

BASE-007 原“真实 MySQL 在线迁移验证待补充”项已在本轮隔离库完成其基线在线执行与版本循环验证；不宣称生产库迁移、生产数据恢复或未来业务迁移均已验收。

### 12.7 命令与实测结果

执行目录：D:\AI\DigiTalent_AI。

```powershell
$env:PYTHONIOENCODING='utf-8'
conda run -n feiyu python --version
conda run -n feiyu python -c "import sys; print(sys.executable)"
conda run -n feiyu python -m pip --version
conda run --no-capture-output -n feiyu python -m tests.mysql_base008_integration_check --allow-isolated-ddl
conda run --no-capture-output -n feiyu python -m pytest -q
conda run --no-capture-output -n feiyu python -m ruff check tests/mysql_base008_integration_check.py
conda run --no-capture-output -n feiyu python -m ruff format --check tests/mysql_base008_integration_check.py
git diff --check
```

- 首轮真实集成脚本：result=PASS，退出码 0，约 5.96 秒；完成授权建库及整轮真实验收。
- 随后补充重复运行的空版本表准入与视图拒绝保护，第二轮真实集成执行 result=PASS，再次验证完整迁移和字段循环；未重复创建数据库。
- 全量 pytest 回归：**121 passed，0 failed，0 skipped**，1.18 秒，退出码 0。与之前保留的 121 项记录分开记录，未将手工 MySQL 验收算入 pytest 项数。
- 真实验收脚本两轮均未失败；预期非法状态、CHECK 和外键拒绝属于成功断言，不计为测试失败。
- Ruff 检查通过，脚本格式检查通过；Git 差异检查通过，只有原有工作区文件换行转换提示。

### 12.8 遗留问题与最终结论

本次授权范围内没有未完成验收项。专用隔离库及空 alembic_version 表保留，后续删除数据库须另行授权；再次执行本脚本会复核数据库状态，非空或有非预期对象时拒绝操作。

本轮仅证明指定本地 MySQL 8.0.44 隔离环境中的公共模型与迁移行为，不替代生产环境验收。后续业务实体引入时仍须独立审查自动生成迁移，特别是自定义类型的渲染与导入。

**最终验收结论：已完成。** 用户原有数据未被清空，业务表未删除，未新增正式业务模型、配置或依赖。报告交付后停止，不进入其他任务。
