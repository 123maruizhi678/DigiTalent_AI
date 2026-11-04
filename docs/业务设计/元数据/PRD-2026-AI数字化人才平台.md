# PRD · 2026 顶配版 AI 数字化人才平台

> 本文档基于两份输入合并生成：
> 1. 《2026 顶配版 AI 数字化人才平台详细技术与功能需求》（`D:\docs\培训\0330\...docx`）—— 产品目标与强制技术规约；
> 2. `D:\project\frontend\ai_talent` 当前代码库（截至 2026-09-27 的源码快照）—— 真实技术栈、模块与接口现状。
>
> 文档目标：把"需求方强制要求"与"团队实际落地"对齐，明确功能边界、技术差距与待决策项，作为后续迭代与验收依据。

---

## 0. 文档状态与阅读指引

| 项 | 内容 |
|---|---|
| 产品名称 | AI 数字化人才平台（仓库 `ai_talent`） |
| 需求来源 | 0330 培训需求 docx（企业级 AI 原生人才智能平台） |
| 当前仓库形态 | Next.js 14 前端 + FastAPI 后端，MVP 已演化为多模块平台 |
| 文档性质 | 产品需求文档（PRD）+ 现状差距分析（Gap Analysis） |
| 关键结论 | 功能覆盖面与需求高度吻合；**技术栈存在可控偏差**（Dify/Vanna.ai/PgSQL 以自研或替代方案落地），需在路线图里确认是否回填 |

> 说明：仓库 README 处于 git 合并冲突残留状态（同时含"简历队列 MVP"与"数智化人才平台"两段），不代表当前架构。本文以 `frontend/src/app/navigation.tsx` 菜单、`backend/app/main.py` 的 28 个路由注册、以及 `pyproject.toml` 依赖为准。

---

## 1. 产品定位与目标

### 1.1 总体定位
企业级 **AI 原生** 数字化人才智能平台，摒弃传统 HR 表单式架构，以 **大模型 AI Agent** 为核心、**RAG 知识库** 为数据底座、**AI 工作流编排** 为业务驱动、**自然语言数据智能分析** 为决策输出，实现人才管理全流程智能化、自动化。

### 1.2 强制架构原则（来自需求，需遵守）
- 前后端分离 + 微服务 + AI 中台 + 多智能体协同。
- 支持私有化部署、国产化适配、高并发、高可用、可横向扩展。
- 数据层 **ORM 全对象映射，杜绝裸 SQL**。
- 指定全套技术栈 **必须全部落地，禁止替换/降级/删减核心组件**（见第 4 节差距分析，当前存在偏差）。

### 1.3 目标用户与角色
| 角色 | 职责 | 对应系统能力 |
|---|---|---|
| 普通员工 | 自助政策问答、测评、学习、查看个人档案 | 知识库分级问答、测评、培训课程、个人画像 |
| HR / 招聘 | 简历筛选、岗位配置、面试、候选人管理 | 简历智能筛选、岗位条件、JD 投放、面试管理、候选人管理 |
| 业务/项目负责人 | 提人才需求、看缺口、做匹配 | 项目人才需求、人才缺口统计、岗位-人才匹配 |
| 管理员 / 运维 | 用户/部门/角色/菜单/模型/智能体配置 | 系统管理全套、模型供应商、Agent 管理、任务调度 |
| 管理层 | 自然语言问数、看决策建议、风险预警 | 智能问数（数据决策）、运营审计 |

---

## 2. 功能模块需求与现状映射

需求文档定义 **6 大业务模块 + RAG 问答 + 权限安全**。以下逐模块列出"需求要求"与"代码现状"的对应关系。

### 2.1 AI 智能人才档案与数字画像
**需求要点**：全格式简历解析（PDF/Word/图片/扫描件，准确率≥99%）、向量级百级标签画像、智能查重合并、语义化自然语言检索、单/批量档案 RAG 问答。

**现状（代码中已落地）**：
- 后端：`resumes`（简历）、`resume_extraction` agent、`talent_profiles`（人才画像）、`candidates`（候选人）、`parsed_resumes` 等表；MinerU + OpenCV + PyPDF 文档解析链路；Milvus 向量库（`vector_store`）。
- 前端：简历智能筛选、简历过滤名单、人才画像档案、数智化运营、候选人管理。
- **匹配度**：高。解析准确率、百级标签体系、查重合并的交互闭环需以测试数据校验（需求量化指标尚未在代码中找到断言）。

### 2.2 AI 智能测评与能力研判
**需求要点**：大模型自适应题库（千人千卷）、全流程自动调度、AI 能力结构分析、动态能力评级、能力雷达图。

**现状**：
- 后端：`exams`（考核）、`exam_paper`（出卷）、`question_bank`（题库）、`wrongbook`（错题复盘）、`exam_results`（成绩）。
- 前端：创建题库、智能出卷、考核成绩、错题与复盘、AI 面试间、复习计划。
- **匹配度**：高（结构与需求一致）。"自适应千人千卷""能力雷达图"的具体算法实现深度需代码复核。

### 2.3 AI 岗位-人才精准匹配
**需求要点**：岗位结构化解析→向量建模、0–100 匹配分（准确率≥90%）、匹配原因可解释、岗位空缺预警与储备推荐。

**现状**：
- 后端：`job_profiles`（岗位条件）、`positions`（岗位）、`job_matching` agent、`talent_gap`（人才缺口）、`match_results`。
- 前端：岗位条件配置、人才缺口统计、简历智能筛选（匹配入口）。
- **匹配度**：高。匹配分值算法与"空缺预警自动推荐"是否闭环需确认。

### 2.4 AI 个性化智能培训成长
**需求要点**：能力缺口诊断、千人千面培训方案、学习全流程管控（防挂机）、成长轨迹可视化。

**现状**：
- 后端：`prejob_training`（岗前培养）、`training_courses`（培训课程）、`review_plan`（复习计划）。
- 前端：岗前培养方案、培训课程、复习计划。
- **匹配度**：中高。防挂机/学时监控等强管控逻辑需确认后端是否有对应校验。

### 2.5 自然语言智能数据决策（Vanna.ai 核心）
**需求要点**：口语化自由问数、自动多维分析、自动出图、一键生成 Word/PDF 报告、智能决策建议、行/字段级权限联动。

**现状**：
- 前端：`data-decision`（智能问数）、运营审计。
- 后端：未检索到 `vanna` 依赖；`observability` 提供指标/审计，但 NL2SQL 引擎归属未明确。
- **匹配度**：⚠️ 中（有"智能问数"入口，但 Vanna.ai 明确的 NL2SQL 能力是否落地、出图/出报告深度需重点确认——见第 4 节差距）。

### 2.6 企业级人才 RAG 智能问答知识库
**需求要点**：100% 私有化、精准无幻觉可溯源、分级权限问答（员工/HR/管理层）。

**现状**：
- 后端：`knowledge_base`（领域知识库）、`knowledge_dao`、Milvus 向量检索、`ai_safety` 护栏。
- 前端：领域知识库、知识库底座、AI 整体架构。
- 额外：引入 **Neo4j**（`graph_store`）做知识图谱，超出需求但增强溯源。
- **匹配度**：高。幻觉抑制与"回答可溯源条款"需以测试验证。

### 2.7 多智能体系统与 Skills 可编排组件库
**需求要点**：五大专属 Agent（档案解析/测评分析/岗位匹配/培训赋能/数据决策）、LangGraph 有状态工作流、可视化编排、多样化触发、Dify 中台统一管控。

**现状**：
- 后端：`agent_management`、`agent_publish`、`agent_workflow`、`business_workflows`、`task_scheduling`（任务调度）、`digital_bot`（数字机器人）、`digital_worker_duties`（数字员工任务）、`langgraph_engine`。
- 前端：Agent 管理、智能体管理、智能体设计、数字员工管理/任务配置、任务调度管理、数字机器人、智能工作台。
- **匹配度**：高（功能面齐全）。但"可视化拖拽编排画布"的成熟度、以及是否等价替代 Dify 需评估（见 4.2）。

### 2.8 多端协同与权限安全体系
**需求要点**：PC+移动端同步、精细化多级权限（角色/行级/字段级）、全操作日志与 AI 调用日志留痕。

**现状**：
- 后端：`user_center`（用户中心）、`operations`（操作）、`observability`（审计）、`model_provider`（模型供应商≈中台入口）。
- 前端：系统管理（用户/部门/角色/菜单/日志）、组织结构、模型供应商、成员 IM 账号管理。
- **匹配度**：高（权限与审计骨架完整）。行级/字段级权限是否贯穿所有查询需逐接口确认。

---

## 3. 系统架构（需求强制分层 vs 实际）

### 3.1 需求强制六层架构
基础设施层 → 数据存储层（MySQL+PgSQL+Milvus+Redis）→ 服务接口层（FastAPI+ORM）→ AI 中台层（Dify+LangChain+LangGraph）→ 智能能力层（RAG/Agent/Vanna/Skills）→ 业务应用层。

### 3.2 实际代码架构（来自 `backend/app/`）
- **服务接口层**：FastAPI，统一 `api` 包下 28 个 router，`/api` 前缀；DTO 用 Pydantic；`exceptions/custom_exception.py` 统一异常；`observability` 全链路日志。✅ 符合。
- **AI 中台层**：未引入 Dify，改为自研 `agent_management / agent_publish / agent_workflow / model_provider` 模块承担"模型管理+Prompt+应用发布+权限"职责。LangGraph 已用（`langgraph_engine`）。
- **智能能力层**：RAG（Milvus+`vector_store`）、Agent（`agent/` 包 + LangGraph）、Skills/编排（`business_workflows`+`task_scheduling`）、NL2SQL（`data-decision`，引擎待确认）。
- **数据存储层**：见第 4 节。
- **业务应用层**：Next.js 前端 `src/react-pages/` 下约 40 个页面，7 大菜单分组。

### 3.3 分层解耦评价
后端包边界清晰（`api → service → dao → infrastructure`，外部依赖经 `tools`/`adapters` 隔离），符合需求"层层解耦、独立可扩展"。原设计文档预期的 PostgreSQL 已被 MySQL 取代，且 worker 由 in-process 异步循环演进为 Celery（见下）。

---

## 4. 技术栈差距分析（核心待决策项）

需求文档以"强制技术栈清单"列出组件，**当前仓库存在以下偏差**，需在路线图阶段决策"回填原栈"还是"以自研/替代方案作为长期架构"。

| 需求强制组件 | 当前代码状态 | 偏差等级 | 建议 |
|---|---|---|---|
| **FastAPI** | ✅ 已用（`fastapi>=0.115`） | 无 | 保持 |
| **ORM（SQLAlchemy）** | ✅ 已用（`sqlalchemy>=2.0`，`dao/infrastructure` 分层） | 无 | 保持，持续排查裸 SQL |
| **MySQL** | ✅ 已用（`pymysql`，业务主数据） | 无 | 保持 |
| **Milvus** | ✅ 已用（`pymilvus>=3.0`，向量检索） | 无 | 保持 |
| **LangGraph** | ✅ 已用（`langgraph>=0.2`，`langgraph_engine`） | 无 | 保持 |
| **Redis** | ⚠️ 经 `celery[redis]` 用于任务调度；**缺统一缓存/会话/限流层** | 中 | 显式引入 Redis 作为缓存与会话/限流中间件，满足热点命中≥98% |
| **PgSQL** | ❌ 未引入，海量分析/时序数据目前落在 MySQL | 高 | 决策：是否引入 PgSQL 做分析宽表/时序（Vanna 类问数更稳）；或确认 MySQL 分区已满足 |
| **Dify** | ❌ 未引入，以自研 `agent_management/agent_publish/agent_workflow/model_provider` 替代 | 高 | 决策：自研中台是否作为长期方案（推荐，可控、贴合业务）；或集成 Dify 做可视化 Prompt/编排 |
| **Vanna.ai** | ❌ 未引入，`data-decision` 模块承载 NL2SQL，引擎未确认 | 高 | 决策：是否基于 Vanna.ai 或自研 NL2SQL；需补"自动出图/出报告"能力 |
| **LangChain** | ⚠️ 未直接声明；`langgraph` 通常随带 `langchain-core` | 低 | 确认依赖树；如需显式 LLM 编排可补 `langchain` |
| **额外已引入** | ✅ Neo4j（知识图谱）、MinIO（对象存储）、MinerU（文档解析）、OpenCV（照片识别）、Celery（异步任务）、NumPy/OpenPyXL | — | 超出需求但增强能力，建议保留并补文档 |

> 结论先行：功能层面偏差小、技术层面偏差集中且**均可控**。最关键的三个决策是 **PgSQL 是否引入、Dify 是否回填、Vanna.ai 是否回填**——建议以"自研中台为主、按需引入 PgSQL 做分析库"的折中路线，既满足需求精神又避免被锁定在单一商业中台。

---

## 5. 数据模型概览（来自 `backend/app/infrastructure/`）

核心表（ORM 模型）已覆盖需求各域，按业务域归类：

| 域 | 代表表 / 模型 | 说明 |
|---|---|---|
| 简历与解析 | `resume_files`、`parse_tasks`、`parse_logs`、`parsed_resumes` | 队列 + 解析结果 |
| 岗位与匹配 | `job_profiles`、`positions`、`match_results` | 岗位条件、匹配分 |
| 人才档案 | `talent_profiles`、`candidates`、`profile_archive` | 画像、候选人 |
| 测评 | `exams`、`exam_paper`、`question_bank`、`wrongbook`、`exam_results` | 题库/出卷/成绩 |
| 培训 | `prejob_training`、`training_courses`、`review_plan` | 培养方案/课程 |
| 项目与需求 | `projects`、`project_demands`、`project_groups` | 项目人才需求 |
| 知识库 | `knowledge_base`（Milvus 向量 + Neo4j 图谱） | RAG 底座 |
| 智能体与任务 | `agent_management`、`agent_publish`、`business_workflows`、`task_scheduling`、`digital_bot`、`digital_worker_duties` | 多智能体/编排 |
| 系统管理 | `user_center`、`operations`、`observability`、部门/角色/菜单 | 权限与审计 |

> 现状 DB 以 MySQL 单库承载上述全部表；需求要求的"四库协同"尚未实现（PgSQL/Redis 专项库缺失）。

---

## 6. API 规范与现状

- **基址与版本**：所有路由以 `/api` 为前缀（如 `/api/resumes`、`/api/agent-management`）。
- **风格**：REST + Pydantic DTO；FastAPI 自动生成 OpenAPI 文档。
- **统一约定（需求要求，代码中部分落地）**：
  - 统一返回格式 / 错误码 / 异常捕获 → `custom_exception.py` ✅
  - 统一权限拦截 → `user_center` + 角色体系（行/字段级待逐接口复核）⚠️
  - 限流/熔断/降级/黑名单 → 仅 Celery 侧有队列限流，**接口级限流未确认** ⚠️
  - SSE 实时推送 → 需求要求；代码中 `observability`/任务轮询存在，SSE 端点需确认 ⚠️
- **已注册路由（28 个）**：resumes, job_profiles, prejob_training, jd_publications, agent_management, digital_worker_duties, interview_invites, candidates, positions, exams, project_demands, project_groups, talent_profiles, projects, business_workflows, multi_round_interviews, observability, knowledge_base, talent_gap, operations, task_scheduling, digital_bot, member_im_account, model_provider, agent_publish, agent_workflow, user_center（另含 agent_management 等）。

---

## 7. 非功能性需求与达标评估

| 指标（需求强制） | 目标值 | 当前评估 |
|---|---|---|
| 并发在线 | ≥2000 人 | 架构支持异步；压测数据缺失 ⚠️ |
| 页面渲染 | ≤1s | 前端 Next.js，待实测 |
| 向量检索 | ≤500ms | Milvus 可达成，待基线测试 ⚠️ |
| 普通接口 | ≤1s；大数据报表 ≤3–5s | FastAPI 异步可达成，待实测 |
| 全年可用率 | ≥99.9%；AI 服务 ≥99.5% | 依赖部署架构（容器化/主从），待建设 |
| 缓存命中率 | ≥98% | 需引入统一 Redis 缓存层 |
| 安全合规 | 网络安全法/数据安全法/个保法；加密/脱敏/备份/防篡改 | 权限+日志骨架在；脱敏/加密专项待补 ⚠️ |
| 国产化适配 | 国产 OS/服务器/数据库 | 未验证（当前 MySQL+Milvus 非国产）⚠️ |
| 检索准确率（RAG） | ≥95% | 待评测集验证 ⚠️ |
| 匹配准确率 | ≥90% | 待评测集验证 ⚠️ |
| 简历解析准确率 | ≥99% | 依赖 MinerU/OpenCV，待实测 ⚠️ |

---

## 8. 实施路线图（建议）

### 阶段一 · 现状夯实（当前→下一里程碑）
1. 修复 README 合并冲突，统一架构说明文档。
2. 逐接口补齐：统一返回/错误码已就位；补 **接口级限流、SSE 实时推送、行/字段级权限拦截**。
3. 建立量化指标基线测试（解析/检索/匹配准确率、响应时延）。

### 阶段二 · 技术栈补齐（按需）
4. 决策并执行：引入 **Redis 统一缓存/会话/限流**；评估 **PgSQL 分析库**。
5. 明确 **Dify / Vanna.ai** 策略：自研中台固化 or 集成商业中台；NL2SQL 引擎选型落地。
6. 安全专项：数据加密、敏感字段脱敏、备份容灾、审计闭环。

### 阶段三 · 能力深化
7. RAG 评测集与幻觉抑制、可溯源条款展示。
8. 多智能体可视化编排画布成熟度提升；Skills 组件市场化。
9. 移动端适配、国产化适配验证、高可用部署（主从/读写分离/容器化）。

### 阶段四 · 交付与售后
10. 数据治理服务（历史数据清洗/向量入库/知识库搭建）、分层培训、质保与 7×24 响应。

---

## 9. 验收口径（Acceptance Criteria）建议

- **功能**：第 2 节 8 大模块均可在真实后端数据下闭环跑通，禁用 mock/固定常量。
- **技术**：第 4 节偏差项给出明确决策记录；若选"回填原栈"，则 Dify/Vanna.ai/PgSQL/Redis 落地并通过集成测试。
- **性能**：第 7 节指标在压测中达标（附测试报告）。
- **安全**：权限三级（角色/行/字段）+ 全量操作与 AI 调用日志，通过安全审计。
- **合规**：满足三部法律要求，出具合规说明。

---

## 10. 待确认 / 风险清单（Open Questions）

1. **Dify 是否回填？** 当前自研中台功能面已覆盖，是否仍需引入 Dify 做可视化 Prompt/编排？
2. **Vanna.ai 是否回填？** `data-decision` 的 NL2SQL 引擎归属与"自动出图/出报告"深度？
3. **PgSQL 是否引入？** 海量分析/时序数据是否继续留在 MySQL？
4. **Redis 专项缓存层**缺失，热点命中率≥98% 如何保障？
5. **行/字段级权限**是否已在所有查询接口落地（需求强制）？
6. **量化指标**（解析/检索/匹配准确率、时延）尚无评测集与基线，验收风险高。
7. **国产化适配**当前技术栈（MySQL/Milvus）非国产，政企场景是否需替换。

---

*生成说明：本文档由需求 docx（功能与强制规约）与 `ai_talent` 仓库源码（frontend/src/app/navigation.tsx、backend/app/main.py、backend/pyproject.toml、backend/app/infrastructure 模型）交叉比对生成，状态截至 2026-09-27。未读取全部业务代码实现细节，故"算法深度/准确率/权限贯穿"等标注 ⚠️ 的项需后续代码复核或测试验证。*
