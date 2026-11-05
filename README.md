# AI 数字化人才平台

本项目采用模块化单体后端（Python、FastAPI、Pydantic Settings）和独立前端（Vue 3、TypeScript、Vite）。当前处于 M0 工程启动与开发基线收尾，技术审核与用户最终确认分别记录，尚未正式关闭。前端保留演示原型，数据库、真实认证、业务 Agent、模型服务和任务调度尚未实现。

## 工程目录

| 路径 | 职责 |
| --- | --- |
| app/api | 总路由与健康检查 |
| app/core | 配置、日志、异常、请求追踪 |
| app/common | 公共能力扩展位置 |
| tests/unit、tests/api | 单元与接口测试 |
| frontend | Vue 前端、测试及构建配置 |
| docs | 设计及开发记录；读取修改须遵守 AGENTS.md 授权边界 |
| quality.py、pyproject.toml | 统一质量入口及 Python 工具配置 |
| requirements/base.txt、requirements/dev.txt | M0 运行、开发依赖及传递依赖精确版本 |

## 环境要求

当前已验证 Windows / PowerShell，Conda `feiyu` 环境 Python 3.11.18；Ruff 兼容基线为 Python 3.11。Node.js v24.21.0、npm 11.19.0。后端使用 FastAPI 0.162.0、Uvicorn 0.54.0、Pydantic 2.14.2、Pydantic Settings 2.16.2；前端精确版本见 package.json 和 package-lock.json，使用 npm ci 复现。

## 后端环境安装

```powershell
Set-Location D:\AI\DigiTalent_AI
conda activate feiyu
python --version
```

运行环境安装：

```powershell
python -m pip install -r requirements/base.txt
```

开发环境安装（包含运行依赖）：

```powershell
python -m pip install -r requirements/dev.txt
```

运行与原开发依赖保留既有版本；新增 pytest-cov 7.1.0 和 coverage 7.17.1 用于后端覆盖率。开发入口通过 `-r base.txt` 包含运行依赖。本轮仅安装上述两个新增包，没有升级、卸载其他依赖；未执行全新环境安装复现。Python 依赖文件统一放入 requirements 目录。

首次配置时（已有 .env 请保留）：

```powershell
if (-not (Test-Path -LiteralPath .env)) { Copy-Item .env.example .env }
```

## 前端环境安装

```powershell
Set-Location D:\AI\DigiTalent_AI\frontend
npm ci
npm run dev
```

构建使用 `npm run build`。标准安装使用 npm ci，保留现有锁文件；本次整改未重新安装依赖。

## 服务启动与健康检查

在已激活 feiyu 的项目根终端启动后端：

```powershell
python -m app.main
```

默认地址 http://127.0.0.1:8080；此入口使用 Settings 的 HOST/PORT。另开终端进入 frontend 执行 `npm run dev`，地址 http://127.0.0.1:5173，端口被占用时会失败。Vite 保留 /api 前缀并代理到 8080；修改后端监听地址时须核对代理配置。

```powershell
Invoke-RestMethod http://127.0.0.1:8080/api/v1/health
Invoke-RestMethod http://127.0.0.1:5173/api/v1/health
```

默认返回 status=ok、service=digitalent-ai，只验证进程健康，不验证外部服务。API_V1_PREFIX 改动后健康路径随之变化。现有未启用的认证 API 扩展点尚需在 M1 统一版本前缀，不能视为真实认证可用。

## 配置说明

`.env.example` 是无真实凭据的中文配置模板；根 `.env` 已被 Git 忽略，模板允许提交。配置入口为 `app/core/config.py`，应用通过 `get_settings()` 读取缓存的不可变 Settings，优先级为进程环境变量 > 根 .env > 默认值。不要在业务代码散落读取环境变量或重复创建配置对象。字段用途、类型、默认值及合法范围见 Field 中文说明与环境模板；新增敏感字段须保护、脱敏，不得提交密码、Token、API Key。

## 自动化测试与构建

已激活 feiyu，在根目录执行：

```powershell
python -m pytest tests -q
python -m ruff check .
python -m ruff format --check .
```

在 frontend 执行：

```powershell
npm run lint
npm run format:check
npm run type-check
npm run test:run
npm run build
```

前端覆盖率可使用 `npm run test:coverage -- --coverage.reportsDirectory=<独立输出目录>`，现有报告须保留。后端覆盖率使用已安装的 pytest-cov：

```powershell
$env:COVERAGE_FILE = "data/quality/coverage/backend/.coverage"
python -m pytest tests -q --cov=app --cov-report=term-missing --cov-report=html:data/quality/coverage/backend/html --cov-report=xml:data/quality/coverage/backend/coverage.xml
Remove-Item Env:COVERAGE_FILE
```

先确认目标目录不存在；重复执行须改用新的独立目录并同步三个输出路径，保留已有报告。

## 统一质量检查

在根目录使用 feiyu Python：

```powershell
python quality.py backend quality-check
python quality.py frontend quality-check
python quality.py all quality-check
```

后端执行 Ruff 检查、格式检查和 pytest；前端执行 lint、格式、类型、Vitest 和构建。失败返回非零退出码；format 命令会修改格式，quality-check 仅检查源码并生成正常构建产物。

## 开发规范

遵循 [AGENTS.md](AGENTS.md)。新任务使用 [统一任务记录模板](docs/开发日记/1104/开发任务记录模板.md)，逐步填写并在完成后形成实际开发报告。报告记录过程及证据，正式设计文档记录已确认的最终设计，不重复维护相同内容。链接不授予 docs 访问权限。

开发完成、测试通过、技术审核通过、用户确认分别记录；自动化通过不代表技术审核或整体验收通过。未经用户确认和明确授权，不自动开始下一任务。

## 当前开发进度

| M0 任务 | 实际交付与状态 |
| --- | --- |
| P6-BASE-001 后端骨架 | 已交付，原验收报告功能标准通过，用户最终确认待定 |
| P6-FE-001 前端骨架 | 已交付，骨架通过；真实 API 接入扩展项待后续处理，用户待确认 |
| P6-BASE-002 统一配置 | 已交付，M0 配置标准通过，用户待确认 |
| P6-BASE-003 日志异常 | 已交付，M0 通用机制通过，业务错误契约等待后续确认，用户待确认 |
| P6-BASE-004 质量工具 | 检查可运行，依赖已统一分离，覆盖率工具已安装并验证；实测结果见验收报告，待审核及确认 |
| P6-BASE-005 开发管理 | 报告和模板已交付，本轮补 README、确认管理方式；待技术审核及用户最终确认 |

收尾实测及遗留项以 [M0 整体验收报告末尾收尾记录](docs/开发日记/1104/M0整体阶段验收报告.md) 为准，历史结论保留。M0 未正式关闭，不自动进入 M1。
