# 01 P6-IAM-001 清理与 MySQL 实施验收记录

日期：2026-11-04。阶段：M1。结论：部分完成，未正式验收；未启动 P6-IAM-002。

## 1. 授权与边界

已应用 digitaltalent-development-workflow Skill，按完整级检查公共数据库基础设施、测试和设计。用户授权本次清理、SQL 编写、测试准备及本目录记录；后续明确批准三表 UUID 使用 CHAR(32)，原文直接修改，不追加设计说明。未获数据库 DDL/DML 执行授权，未连接或修改数据库。

开发前 Git 工作区已有大量修改、删除与未跟踪文件；包括 ORM、数据库基础代码、SQL 占位文件及设计目录。没有覆盖无关改动，没有提交 Git，没有安装或升级依赖。共享文件 tests/conftest.py 仅新增显式 MySQL 测试命令行参数，保留既有环境隔离机制；生产配置、应用入口及已有 ORM 均未改动。已核对相关 git log、git diff、调用及测试关系。

## 2. 第一阶段交付

修改清单：

| 文件 | 本次变更 |
|---|---|
| tests/unit/test_database.py | 去除替代数据库引擎，保留连接检查、SELECT 1、上下文释放及关闭状态断言 |
| tests/unit/test_orm.py | 保留元数据测试，将全部实际写入与查询测试移至显式 MySQL 验收入口，去除自动建表夹具 |
| tests/conftest.py | 新增独立配置、确认库名及明确写入授权参数，无隐式业务库回退 |

新增 tests/mysql_orm_check.py，保留原有10项参数化后的业务行为验证：100个UUID唯一性与查询往返、UUID JSON/外键值、UTC与微秒、更新行为、独立Mixin写入查询、无时区拒绝、状态默认/合法变更、三种非法状态、业务枚举混用拒绝、数据库CHECK及服务端默认值。未删除这些测试要求，未添加 skip，未降低断言。实际MySQL约束效果待执行。

删除文件清单：无。未发现需要删除的专属依赖或配置，未改依赖版本。

检查命令：

- rg -n -i 'sqlite|create_all' app tests requirements sql .env.example README.md：无匹配（生成本报告前）。
- rg -l -i 'sqlite' --glob '!docs/**' --glob '!logs/**' --glob '!scripts/**' --glob '!data/**' --glob '!frontend/node_modules/**' --glob '!frontend/dist/**' --glob '!*.lock' .：无匹配。
- 指定数据库设计目录、架构主文档、开发管理主文档 Select-String SQLite：无匹配。

检查范围：用户指定五份数据库设计文档、docs/02_系统架构设计/*.md、docs/06_开发与测试管理/*.md，以及当前代码、测试、依赖和配置。未扫描 docs 全目录、logs、scripts、data、架构可行性子目录及历史开发记录。未明确文件路径的当前实施方案尚未核查，已发出路径澄清问题，未获路径回复；无法声称整个仓库所有文档均已清零。本报告按交付要求记载清理结果，本身不是正式数据库设计。

阶段结论：已发现的两处实现已清理，授权核查范围无残留；全项目彻底清理仍待补齐受限范围核查证据。

## 3. 第二阶段交付与一致性审核

| 文件 | 交付 |
|---|---|
| sql/init.sql | 人工编排三表、全部38列、3PK、7唯一索引、4普通索引、3FK、12CHECK、4虚拟生成列及3触发器 |
| sql/test_common_models.sql | 人工维护4张公共Mixin测试辅助表；仅用于独立测试库 |
| sql/README.md | 环境准入、执行顺序、授权、测试命令与回退边界 |
| tests/unit/test_iam_sql.py | SQL/ORM静态一致性断言，不连接数据库 |
| tests/mysql_orm_check.py | 公共模型10项MySQL行为用例 |
| tests/mysql_iam_check.py | IAM默认/关联查询、生成列、CHECK、唯一性、删除释放、FK和3触发器，共10项用例 |

数据库设计修改清单：docs/03_数据库设计/00_数据库技术方案_V1.1.md、01_数据库总体设计_V1.1.md、02_数据库详细设计_V1.1.md、03_用户与组织数据模型详细设计_V1.3.md 中 CHAR(36) 原文统一为用户批准的 CHAR(32)。审核报告内容未扩写。未重复开发ORM。

SQL 是手工编排的DDL，未调用 CreateTable 自动生成作为交付；长文本规范化与邀请CHECK表达式复用现有谓词逐项核对。静态测试按ORM字段逐列核对类型/长度、NULL、服务端默认、生成表达式，以及全部已声明索引、CHECK和FK名称/字段/行为。NULL列默认NULL，UUID与DATETIME(6)均无服务端生成默认；客户端UUID4/utc_now/onupdate继续由公共Mixin负责。

表引擎/排序规则：三表均 InnoDB、utf8mb4、utf8mb4_0900_bin。布尔类型BOOLEAN与MySQL TINYINT(1)同义，默认0并受CHECK限制。有效唯一由active_key在删除时置NULL释放；主要归属由primary_user_id生成列唯一保证；NULL邮箱/电话及多轮历史不占有效唯一值。全部外键RESTRICT/RESTRICT，无物理级联。

三个触发器分别作用于三表BEFORE UPDATE：OLD.is_deleted=1且NEW.is_deleted=0时SIGNAL 45000；主键发生变化也SIGNAL。触发器是显式SQL对象，不属于ORM metadata。未添加跨表更新、树递归或未经批准的业务规则。

审核结论：静态核对一致；三个触发器SQL已完成。尚无MySQL服务器解析、实际结构、约束及执行证据，不能等同于独立人工审批通过或正式验收。

## 4. 环境、实际命令与结果

Conda：feiyu；Python：3.11.18；解释器：D:\anaconda3\envs\feiyu\python.exe；pip 26.2.2：D:\anaconda3\envs\feiyu\Lib\site-packages\pip。

已执行：conda env list；conda run -n feiyu python --version；conda run -n feiyu python -c "import sys; print(sys.executable)"；conda run -n feiyu python -m pip --version，均确认属于feiyu。

| 验证 | 真实结果 |
|---|---|
| conda run -n feiyu python -m pytest -q | 最终105 passed，1.37秒，退出0 |
| conda run -n feiyu python -m pytest --collect-only -q tests/mysql_orm_check.py tests/mysql_iam_check.py | 20 tests collected，退出0；仅收集，不是运行通过 |
| conda run -n feiyu python -m ruff check tests/conftest.py tests/unit/test_orm.py tests/unit/test_database.py tests/unit/test_iam_sql.py tests/mysql_orm_check.py tests/mysql_iam_check.py | All checks passed，退出0 |
| 同一6文件的 conda run -n feiyu python -m ruff format --check | 最终6 files already formatted，退出0 |
| git diff --check | 退出0；仅已有文件换行提示 |

过程中问题及修复：PowerShell花括号通配命令解析失败，改用明确路径；首次通过Conda标准输入的编辑命令未产生文件变更，核查后改为临时文件执行并删除临时文件。Ruff曾报告导入fixture名称重定义，改为委托fixture。新增SQL审核测试首次104通过/1失败，原因是SQLAlchemy枚举约束带表限定名，使用include_table=False正确对比同一CHECK，随后105通过。格式检查曾有1文件未格式化，格式化后6文件通过。未删除原断言来制造通过结果。

## 5. MySQL测试方案与未执行清单

先由用户确认独立MySQL测试实例、库名及专用账号，审核并授权SQL；人工执行init.sql与test_common_models.sql准备空白测试库；使用sql/README.md中的显式命令运行20项用例。夹具检查目标库名与配置一致、库名以_test结尾且不是agent_service、8.0.17+及严格模式，每个测试外层事务回滚。此保护不能代替人工隔离确认。现有统一Settings配置复用，无新增应用配置字段或环境变量。

尚未执行/待补充验收：

1. 独立审核人与执行人审阅SQL；确认MySQL版本、严格模式、排序规则、最小权限与主库路由。
2. 授权后实际建表，留存38列、14索引、3FK、12CHECK、4生成列、3触发器的SHOW CREATE/元数据证据。
3. 运行20项MySQL用例，验证公共字段、UUID、时区、CHECK、FK、唯一/历史释放、生成列、触发器及关联查询。
4. 补齐全部12CHECK逐一负例、全部唯一键及NULL/多轮历史、三FK删除更新RESTRICT、大小写/重音/尾空格/规范化边界、邀请元组边界、并发双主要测试；现有代码只覆盖部分代表性约束，不能当作完整覆盖。
5. 按V1.3后续事务范围补足并发树、邀请竞争、命名锁、审计故障等必要验证；本轮未实现Service/Repository/API，不宣称已验证其事务规则。
6. 补齐未明确路径实施文档的授权核查；复核本次三表及SQL静态审核证据并申请正式验收。

## 6. 最终状态

1. SQLite：已发现实现已清理，授权核查范围无残留；完整仓库清零尚未证实。
2. 原有效测试要求：保留；10项实际数据库行为转入MySQL显式验收，未运行，未跳过冒充通过。
3. 三表建表SQL及三个触发器：已完成编写。
4. SQL与ORM：静态核对一致，实际MySQL一致性尚未验证。
5. MySQL实际建表、DDL/DML及约束验证：均未执行，没有创建测试库或修改现有结构。
6. P6-IAM-001：M1阶段部分完成，未正式验收；待隔离MySQL验证、覆盖补齐、人工审核及证据齐备后申请验收。
7. P6-IAM-002：未启动。

任务本轮交付后停止，等待用户确认。


## 7. 2026-11-04 正式建表与 ORM 一致性核查报告（本轮追加）

本节为本轮实际执行结果，前文“未连接、未执行DDL、实际一致性尚未验证”等表述保留为历史阶段记录，以本节更新当前实施状态。

### 7.1 授权、影响与执行方案

用户明确授权在现有 agent_service 中执行 sql/init.sql 及必要只读结构核查，并指定本文件更新开发记录。本报告合并追加至指定文件，未访问其他 docs 文件。应用 digitaltalent-development-workflow Skill，执行等级：完整（数据库基础设施）。只执行人工 SQL 的三表及三个触发器，不修改应用、配置、ORM、依赖或建表SQL。

调用链：get_settings() → Database.engine → MySQL；register_models() → Base.metadata → SQLAlchemy Inspector/只读 information_schema 与 SHOW CREATE → 对比。没有调用 metadata.create_all 或 Alembic。

预检确认 DATABASE()=agent_service，MySQL 8.0.44，所有表、索引、触发器清单均为空；严格模式 STRICT_TRANS_TABLES 已启用（同时包含 ONLY_FULL_GROUP_BY、NO_ZERO_IN_DATE、NO_ZERO_DATE、ERROR_FOR_DIVISION_BY_ZERO、NO_ENGINE_SUBSTITUTION）。库默认 utf8mb4/utf8mb4_0900_ai_ci，三表均由 SQL 显式指定 utf8mb4_0900_bin，无库配置变更。连接配置复用 app/core/config.py 的 get_settings 和 app/core/database.py 的 Database；使用 MYSQL_HOST、MYSQL_PORT、MYSQL_USER、MYSQL_PASSWORD、MYSQL_DATABASE 及既有连接池/超时项，不记录凭据或完整连接串。

DDL 隐式提交，不能依赖事务回滚；若中途失败应停止并保留现场，本轮无SQL执行异常，未执行任何删除回退。未查询或修改业务数据。

### 7.2 正式执行结果

六条 CREATE 全部成功（按原SQL顺序解析 DELIMITER，逐条原文提交，未自动生成DDL）。

| 对象 | 列 | 主键 | 唯一索引 | 普通索引 | 外键 | CHECK | 虚拟生成列 | 触发器 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| sys_organization | 10 | 1 | 1 | 1 | 1 | 5 | 1 | 1 |
| sys_user | 19 | 1 | 4 | 1 | 0 | 6 | 1 | 1 |
| sys_user_organization | 9 | 1 | 2 | 2 | 2 | 1 | 2 | 1 |
| 合计 | 38 | 3 | 7 | 4 | 3 | 12 | 4 | 3 |

### 7.3 ORM 一致性核查

146项结构比较通过：字段集合、MySQL方言编译后的类型/长度/DATETIME(6)精度、NULL、服务端默认值、主键字段、全部11个非主键索引的名称/顺序/唯一性、3外键名称/引用/RESTRICT行为、生成表达式及VIRTUAL属性、CHECK名称、引擎及排序规则、触发器时机/事件/正文。3个触发器逐一对应其业务表，均为 BEFORE UPDATE，正文与init.sql一致。

12个CHECK均ENFORCED=YES，额外12项表达式词元比较通过：规范化服务器反引号、字符集前缀、十六进制字面量表示、转义和冗余括号；括号分组另按保留的定义复核，包含邀请OR/AND分支。该比较不等同于行为或负例测试。

预期表示差异：BOOLEAN对应MySQL TINYINT(1)；UUID对应CHAR(32)；UTCDateTime对应DATETIME(6)；MySQL主键名称PRIMARY，与ORM命名约定的pk_*不同；ORM字段comment未在人工SQL中声明。以上已明确记录，字段映射与约束无实质差异。客户端UUID4、UTC默认及onupdate不是服务端默认；触发器由人工SQL维护，不在ORM metadata内。列物理顺序可不同，按字段名核对。未将Python层时间处理视为已完成数据库往返验证。

### 7.4 环境、命令及验证结果

Conda feiyu；Python 3.11.18；解释器 D:\anaconda3\envs\feiyu\python.exe；pip 26.2.2，路径 D:\anaconda3\envs\feiyu\Lib\site-packages\pip。未安装依赖。

执行目录 D:\AI\DigiTalent_AI。实际命令：

```powershell
conda env list
conda run -n feiyu python --version
conda run -n feiyu python -c "import sys; print(sys.executable)"
conda run -n feiyu python -m pip --version
$env:PYTHONPATH=(Get-Location).Path
conda run -n feiyu python $env:TEMP/p6_iam_preflight.py
conda run -n feiyu python $env:TEMP/p6_iam_execute.py
conda run -n feiyu python $env:TEMP/p6_iam_verify.py
conda run -n feiyu python $env:TEMP/p6_iam_checks.py
conda run -n feiyu python -m pytest -q tests/unit/test_iam_sql.py tests/unit/test_iam_models.py
```

预检、六条DDL、最终146项结构核对、12项CHECK词元核对均退出0；pytest：5 passed in 0.62s，退出0。临时核查脚本首次比较遇到反射字符串附带COLLATE、Boolean别名、DATETIME精度展示差异，分别退出1；修正为MySQL方言编译后独立核对类型和表排序规则，最终通过。以上是核查脚本表示处理问题，没有再次执行DDL或修改数据库结构。

未执行 sql/test_common_models.sql、MySQL专项测试及行为测试；未运行任何测试DML。未修改业务代码，回归仅执行上述5项相关静态单元测试。建表与元数据一致不证明约束负例、触发器行为或并发事务正确。

### 7.5 Git与交付范围

开发前 git status --short 显示大量已有修改/删除/未跟踪文件；包括.env.example、AGENTS.md、app/api/health.py、app/core/config.py、app/main.py及docs历史目录等。本轮保留全部原有工作，仅在本文件末尾追加实施报告；没有删除文件，没有提交Git。非docs已有受跟踪变更统计为11文件、378新增/118删除；本轮不改变这些代码。临时执行/核对脚本与原始JSON保存在系统TEMP，不作为项目源码交付；以下内嵌结构证据作为持久记录。

### 7.6 状态与待人工验收

本次建表及实际结构核对：已完成。P6-IAM-001总体结论：部分完成，尚未正式验收。后续仍需在另行授权、准备好的隔离MySQL测试库执行行为测试、补齐既有记录列出的边界及并发覆盖并进行人工审核；本次不申请或宣布正式验收通过。P6-IAM-002未启动。无本轮未解决的建表执行异常。

执行时间（系统记录）：2026-11-04 21:37:49.701222+08:00；SQL SHA256：`ce1530702e1f73920827c638728557fb160a5b24f246452838f0364036b9ab85`。

### 7.7 实际 SHOW CREATE TABLE 证据

#### sys_organization

```sql
CREATE TABLE `sys_organization` (
  `id` char(32) COLLATE utf8mb4_0900_bin NOT NULL,
  `organization_code` varchar(64) COLLATE utf8mb4_0900_bin NOT NULL,
  `organization_name` varchar(200) COLLATE utf8mb4_0900_bin NOT NULL,
  `organization_type` varchar(32) COLLATE utf8mb4_0900_bin NOT NULL,
  `parent_id` char(32) COLLATE utf8mb4_0900_bin DEFAULT NULL,
  `status` varchar(8) COLLATE utf8mb4_0900_bin NOT NULL DEFAULT 'active',
  `is_deleted` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `active_key` tinyint GENERATED ALWAYS AS ((case when (`is_deleted` = 0) then 1 else NULL end)) VIRTUAL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_sys_organization_code_active` (`organization_code`,`active_key`),
  KEY `ix_sys_org_parent_deleted_status` (`parent_id`,`is_deleted`,`status`),
  CONSTRAINT `fk_sys_org_parent` FOREIGN KEY (`parent_id`) REFERENCES `sys_organization` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `ck_sys_organization_deleted` CHECK ((`is_deleted` in (0,1))),
  CONSTRAINT `ck_sys_organization_not_self` CHECK (((`parent_id` is null) or (`parent_id` <> `id`))),
  CONSTRAINT `ck_sys_organization_record_status` CHECK ((`status` in (_utf8mb4'active',_utf8mb4'inactive'))),
  CONSTRAINT `ck_sys_organization_root` CHECK ((((`organization_type` = _utf8mb4'group') and (`parent_id` is null)) or (`organization_type` = _utf8mb4'company') or ((`organization_type` = _utf8mb4'department') and (`parent_id` is not null)))),
  CONSTRAINT `ck_sys_organization_type_and_text` CHECK (((`organization_type` in (_utf8mb4'group',_utf8mb4'company',_utf8mb4'department')) and (`organization_code` is not null) and (char_length(`organization_code`) > 0) and (not(regexp_like(`organization_code`,convert(0x5e5b5c787b303030397d2d5c787b303030447d5c787b303031437d2d5c787b303032307d5c787b303038357d5c787b303041307d5c787b313638307d5c787b323030307d2d5c787b323030417d5c787b323032387d5c787b323032397d5c787b323032467d5c787b323035467d5c787b333030307d5d7c5b5c787b303030397d2d5c787b303030447d5c787b303031437d2d5c787b303032307d5c787b303038357d5c787b303041307d5c787b313638307d5c787b323030307d2d5c787b323030417d5c787b323032387d5c787b323032397d5c787b323032467d5c787b323035467d5c787b333030307d5d247c5b5c707b43637d5c707b43667d5d using utf8mb4),_utf8mb4'c'))) and (not(regexp_like(`organization_code`,convert(0x5b5c787b303030397d2d5c787b303030447d5c787b303031437d2d5c787b303032307d5c787b303038357d5c787b303041307d5c787b313638307d5c787b323030307d2d5c787b323030417d5c787b323032387d5c787b323032397d5c787b323032467d5c787b323035467d5c787b333030307d5d using utf8mb4),_utf8mb4'c'))) and (`organization_name` is not null) and (char_length(`organization_name`) > 0) and (not(regexp_like(`organization_name`,convert(0x5e5b5c787b303030397d2d5c787b303030447d5c787b303031437d2d5c787b303032307d5c787b303038357d5c787b303041307d5c787b313638307d5c787b323030307d2d5c787b323030417d5c787b323032387d5c787b323032397d5c787b323032467d5c787b323035467d5c787b333030307d5d7c5b5c787b303030397d2d5c787b303030447d5c787b303031437d2d5c787b303032307d5c787b303038357d5c787b303041307d5c787b313638307d5c787b323030307d2d5c787b323030417d5c787b323032387d5c787b323032397d5c787b323032467d5c787b323035467d5c787b333030307d5d247c5b5c707b43637d5c707b43667d5d using utf8mb4),_utf8mb4'c')))))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_bin;
```

#### sys_user

```sql
CREATE TABLE `sys_user` (
  `id` char(32) COLLATE utf8mb4_0900_bin NOT NULL,
  `username` varchar(64) COLLATE utf8mb4_0900_bin NOT NULL,
  `real_name` varchar(100) COLLATE utf8mb4_0900_bin NOT NULL,
  `nickname` varchar(100) COLLATE utf8mb4_0900_bin DEFAULT NULL,
  `display_name` varchar(100) COLLATE utf8mb4_0900_bin DEFAULT NULL,
  `email` varchar(254) COLLATE utf8mb4_0900_bin DEFAULT NULL,
  `phone` varchar(16) COLLATE utf8mb4_0900_bin DEFAULT NULL,
  `password_hash` varchar(512) COLLATE utf8mb4_0900_bin DEFAULT NULL,
  `status` varchar(8) COLLATE utf8mb4_0900_bin NOT NULL DEFAULT 'inactive',
  `is_deleted` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `invitation_token_hash` char(64) COLLATE utf8mb4_0900_bin DEFAULT NULL,
  `invitation_issued_at` datetime(6) DEFAULT NULL,
  `invitation_expires_at` datetime(6) DEFAULT NULL,
  `invitation_sent_at` datetime(6) DEFAULT NULL,
  `invitation_accepted_at` datetime(6) DEFAULT NULL,
  `invitation_revoked_at` datetime(6) DEFAULT NULL,
  `active_key` tinyint GENERATED ALWAYS AS ((case when (`is_deleted` = 0) then 1 else NULL end)) VIRTUAL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_sys_user_invitation_hash` (`invitation_token_hash`),
  UNIQUE KEY `uq_sys_user_username_active` (`username`,`active_key`),
  UNIQUE KEY `uq_sys_user_email_active` (`email`,`active_key`),
  UNIQUE KEY `uq_sys_user_phone_active` (`phone`,`active_key`),
  KEY `ix_sys_user_deleted_status` (`is_deleted`,`status`),
  CONSTRAINT `ck_sys_user_activation` CHECK ((((`status` <> _utf8mb4'active') or (`password_hash` is not null)) and ((`invitation_accepted_at` is null) or (`password_hash` is not null)))),
  CONSTRAINT `ck_sys_user_deleted` CHECK ((`is_deleted` in (0,1))),
  CONSTRAINT `ck_sys_user_invitation` CHECK (((((`invitation_issued_at` is null) and (`invitation_token_hash` is null) and (`invitation_expires_at` is null) and (`invitation_sent_at` is null) and (`invitation_accepted_at` is null) and (`invitation_revoked_at` is null)) or ((`invitation_issued_at` is not null) and (`invitation_expires_at` is not null) and (`invitation_expires_at` > `invitation_issued_at`) and ((`invitation_sent_at` is null) or (`invitation_sent_at` >= `invitation_issued_at`)) and ((`invitation_accepted_at` is null) or ((`invitation_accepted_at` >= `invitation_issued_at`) and (`invitation_accepted_at` < `invitation_expires_at`))) and ((`invitation_revoked_at` is null) or (`invitation_revoked_at` >= `invitation_issued_at`)) and ((`invitation_accepted_at` is null) or (`invitation_revoked_at` is null)) and (((`invitation_accepted_at` is null) and (`invitation_revoked_at` is null)) or (`invitation_token_hash` is null)) and ((`invitation_accepted_at` is not null) or (`invitation_revoked_at` is not null) or (`is_deleted` = 1) or (`invitation_token_hash` is not null)))) and ((`invitation_token_hash` is null) or ((char_length(`invitation_token_hash`) = 64) and (not(regexp_like(`invitation_token_hash`,convert(0x5b5e302d39612d665d using utf8mb4),_utf8mb4'c'))))))),
  CONSTRAINT `ck_sys_user_optional_text` CHECK ((((`nickname` is null) or ((`nickname` is not null) and (char_length(`nickname`) > 0) and (not(regexp_like(`nickname`,convert(0x5e5b5c787b303030397d2d5c787b303030447d5c787b303031437d2d5c787b303032307d5c787b303038357d5c787b303041307d5c787b313638307d5c787b323030307d2d5c787b323030417d5c787b323032387d5c787b323032397d5c787b323032467d5c787b323035467d5c787b333030307d5d7c5b5c787b303030397d2d5c787b303030447d5c787b303031437d2d5c787b303032307d5c787b303038357d5c787b303041307d5c787b313638307d5c787b323030307d2d5c787b323030417d5c787b323032387d5c787b323032397d5c787b323032467d5c787b323035467d5c787b333030307d5d247c5b5c707b43637d5c707b43667d5d using utf8mb4),_utf8mb4'c'))))) and ((`display_name` is null) or ((`display_name` is not null) and (char_length(`display_name`) > 0) and (not(regexp_like(`display_name`,convert(0x5e5b5c787b303030397d2d5c787b303030447d5c787b303031437d2d5c787b303032307d5c787b303038357d5c787b303041307d5c787b313638307d5c787b323030307d2d5c787b323030417d5c787b323032387d5c787b323032397d5c787b323032467d5c787b323035467d5c787b333030307d5d7c5b5c787b303030397d2d5c787b303030447d5c787b303031437d2d5c787b303032307d5c787b303038357d5c787b303041307d5c787b313638307d5c787b323030307d2d5c787b323030417d5c787b323032387d5c787b323032397d5c787b323032467d5c787b323035467d5c787b333030307d5d247c5b5c707b43637d5c707b43667d5d using utf8mb4),_utf8mb4'c'))))) and ((`email` is null) or ((`email` is not null) and (char_length(`email`) > 0) and (not(regexp_like(`email`,convert(0x5e5b5c787b303030397d2d5c787b303030447d5c787b303031437d2d5c787b303032307d5c787b303038357d5c787b303041307d5c787b313638307d5c787b323030307d2d5c787b323030417d5c787b323032387d5c787b323032397d5c787b323032467d5c787b323035467d5c787b333030307d5d7c5b5c787b303030397d2d5c787b303030447d5c787b303031437d2d5c787b303032307d5c787b303038357d5c787b303041307d5c787b313638307d5c787b323030307d2d5c787b323030417d5c787b323032387d5c787b323032397d5c787b323032467d5c787b323035467d5c787b333030307d5d247c5b5c707b43637d5c707b43667d5d using utf8mb4),_utf8mb4'c'))) and (not(regexp_like(`email`,convert(0x5b5e212d7e5d using utf8mb4),_utf8mb4'c'))) and (`email` = (lower(`email`) collate utf8mb4_0900_bin)) and ((char_length(`email`) - char_length(replace(`email`,_utf8mb4'@',_utf8mb4''))) = 1) and (left(`email`,1) <> _utf8mb4'@') and (right(`email`,1) <> _utf8mb4'@'))) and ((`phone` is null) or ((`phone` is not null) and (char_length(`phone`) > 0) and (not(regexp_like(`phone`,convert(0x5e5b5c787b303030397d2d5c787b303030447d5c787b303031437d2d5c787b303032307d5c787b303038357d5c787b303041307d5c787b313638307d5c787b323030307d2d5c787b323030417d5c787b323032387d5c787b323032397d5c787b323032467d5c787b323035467d5c787b333030307d5d7c5b5c787b303030397d2d5c787b303030447d5c787b303031437d2d5c787b303032307d5c787b303038357d5c787b303041307d5c787b313638307d5c787b323030307d2d5c787b323030417d5c787b323032387d5c787b323032397d5c787b323032467d5c787b323035467d5c787b333030307d5d247c5b5c707b43637d5c707b43667d5d using utf8mb4),_utf8mb4'c'))) and regexp_like(`phone`,convert(0x5e5b2b5d5b312d395d5b302d395d7b302c31347d24 using utf8mb4),_utf8mb4'c'))) and ((`password_hash` is null) or ((char_length(`password_hash`) between 1 and 512) and (`password_hash` is not null) and (char_length(`password_hash`) > 0) and (not(regexp_like(`password_hash`,convert(0x5e5b5c787b303030397d2d5c787b303030447d5c787b303031437d2d5c787b303032307d5c787b303038357d5c787b303041307d5c787b313638307d5c787b323030307d2d5c787b323030417d5c787b323032387d5c787b323032397d5c787b323032467d5c787b323035467d5c787b333030307d5d7c5b5c787b303030397d2d5c787b303030447d5c787b303031437d2d5c787b303032307d5c787b303038357d5c787b303041307d5c787b313638307d5c787b323030307d2d5c787b323030417d5c787b323032387d5c787b323032397d5c787b323032467d5c787b323035467d5c787b333030307d5d247c5b5c707b43637d5c707b43667d5d using utf8mb4),_utf8mb4'c'))) and (not(regexp_like(`password_hash`,convert(0x5b5e212d7e5d using utf8mb4),_utf8mb4'c'))))))),
  CONSTRAINT `ck_sys_user_required_text` CHECK (((`username` is not null) and (char_length(`username`) > 0) and (not(regexp_like(`username`,convert(0x5e5b5c787b303030397d2d5c787b303030447d5c787b303031437d2d5c787b303032307d5c787b303038357d5c787b303041307d5c787b313638307d5c787b323030307d2d5c787b323030417d5c787b323032387d5c787b323032397d5c787b323032467d5c787b323035467d5c787b333030307d5d7c5b5c787b303030397d2d5c787b303030447d5c787b303031437d2d5c787b303032307d5c787b303038357d5c787b303041307d5c787b313638307d5c787b323030307d2d5c787b323030417d5c787b323032387d5c787b323032397d5c787b323032467d5c787b323035467d5c787b333030307d5d247c5b5c707b43637d5c707b43667d5d using utf8mb4),_utf8mb4'c'))) and (not(regexp_like(`username`,convert(0x5b5c787b303030397d2d5c787b303030447d5c787b303031437d2d5c787b303032307d5c787b303038357d5c787b303041307d5c787b313638307d5c787b323030307d2d5c787b323030417d5c787b323032387d5c787b323032397d5c787b323032467d5c787b323035467d5c787b333030307d5d using utf8mb4),_utf8mb4'c'))) and (`real_name` is not null) and (char_length(`real_name`) > 0) and (not(regexp_like(`real_name`,convert(0x5e5b5c787b303030397d2d5c787b303030447d5c787b303031437d2d5c787b303032307d5c787b303038357d5c787b303041307d5c787b313638307d5c787b323030307d2d5c787b323030417d5c787b323032387d5c787b323032397d5c787b323032467d5c787b323035467d5c787b333030307d5d7c5b5c787b303030397d2d5c787b303030447d5c787b303031437d2d5c787b303032307d5c787b303038357d5c787b303041307d5c787b313638307d5c787b323030307d2d5c787b323030417d5c787b323032387d5c787b323032397d5c787b323032467d5c787b323035467d5c787b333030307d5d247c5b5c707b43637d5c707b43667d5d using utf8mb4),_utf8mb4'c'))))),
  CONSTRAINT `ck_sys_user_status` CHECK ((`status` in (_utf8mb4'active',_utf8mb4'inactive',_utf8mb4'locked')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_bin;
```

#### sys_user_organization

```sql
CREATE TABLE `sys_user_organization` (
  `id` char(32) COLLATE utf8mb4_0900_bin NOT NULL,
  `user_id` char(32) COLLATE utf8mb4_0900_bin NOT NULL,
  `organization_id` char(32) COLLATE utf8mb4_0900_bin NOT NULL,
  `is_primary` tinyint(1) NOT NULL DEFAULT '0',
  `is_deleted` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `active_key` tinyint GENERATED ALWAYS AS ((case when (`is_deleted` = 0) then 1 else NULL end)) VIRTUAL,
  `primary_user_id` char(32) COLLATE utf8mb4_0900_bin GENERATED ALWAYS AS ((case when ((`is_deleted` = 0) and (`is_primary` = 1)) then `user_id` else NULL end)) VIRTUAL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_sys_user_org_active` (`user_id`,`organization_id`,`active_key`),
  UNIQUE KEY `uq_sys_user_org_primary` (`primary_user_id`),
  KEY `ix_sys_user_org_user_deleted_primary` (`user_id`,`is_deleted`,`is_primary`),
  KEY `ix_sys_user_org_org_deleted_user` (`organization_id`,`is_deleted`,`user_id`),
  CONSTRAINT `fk_sys_user_org_org` FOREIGN KEY (`organization_id`) REFERENCES `sys_organization` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_sys_user_org_user` FOREIGN KEY (`user_id`) REFERENCES `sys_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `ck_sys_user_organization_flags` CHECK (((`is_deleted` in (0,1)) and (`is_primary` in (0,1))))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_bin;
```

### 7.8 触发器与CHECK执行状态证据

```sql
CREATE TRIGGER trg_sys_organization_before_update BEFORE UPDATE ON sys_organization FOR EACH ROW
BEGIN
    IF OLD.is_deleted=1 AND NEW.is_deleted=0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Deleted organization cannot be restored';
    END IF;
    IF NOT (OLD.id <=> NEW.id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Organization id is immutable';
    END IF;
END
```

```sql
CREATE TRIGGER trg_sys_user_before_update BEFORE UPDATE ON sys_user FOR EACH ROW
BEGIN
    IF OLD.is_deleted=1 AND NEW.is_deleted=0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Deleted user cannot be restored';
    END IF;
    IF NOT (OLD.id <=> NEW.id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='User id is immutable';
    END IF;
END
```

```sql
CREATE TRIGGER trg_sys_user_organization_before_update BEFORE UPDATE ON sys_user_organization FOR EACH ROW
BEGIN
    IF OLD.is_deleted=1 AND NEW.is_deleted=0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Deleted membership cannot be restored';
    END IF;
    IF NOT (OLD.id <=> NEW.id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Membership id is immutable';
    END IF;
END
```

12个CHECK的ENFORCED核查结果：

- ck_sys_organization_deleted：YES
- ck_sys_organization_type_and_text：YES
- ck_sys_organization_not_self：YES
- ck_sys_organization_root：YES
- ck_sys_organization_record_status：YES
- ck_sys_user_deleted：YES
- ck_sys_user_required_text：YES
- ck_sys_user_optional_text：YES
- ck_sys_user_status：YES
- ck_sys_user_activation：YES
- ck_sys_user_invitation：YES
- ck_sys_user_organization_flags：YES
