# P6-BASE-004：建立代码规范与质量工具

- 日期：2026-11-04（Asia/Shanghai）。
- 状态：质量工具及入口已建立，前端历史格式问题阻塞完整验收；等待用户审核，不进入 BASE-005。
- 仅访问用户指定的五份开发依据和根 AGENTS.md；未扫描 docs、logs、scripts、data。

## 1. 原有工具与版本核对

后端实际布局为根 app/、tests/unit/、tests/api/，不迁移。requirements.txt 为既有精确版本依赖清单，包含 Ruff 0.17.3、pytest 8.4.2、pytest-asyncio 0.26.0。原无 Ruff/pytest 项目配置或统一入口，已有 51 项测试。默认 python 为 3.13.5，实际验收使用 D:/anaconda3/envs/feiyu/python.exe（3.11.18），未升级解释器。

feiyu 原未安装 Ruff，本次仅执行 pip install --no-deps ruff==0.17.3，使用已有明确基线，无新增依赖声明或依赖升级。已有环境与 requirements 存在无关版本差异，如 langchain 实装 1.4.8/声明 1.4.7、langchain-core 实装 1.7.4/声明 1.7.3；未自行同步这些无关依赖。requirements 原为综合环境清单，未借本任务重构运行/开发依赖分类。

前端 Node v24.21.0、npm 11.19.0；ESLint 10.14.0、eslint-plugin-vue 10.12.0、typescript-eslint 8.72.1、eslint-config-prettier 10.1.8、Prettier 3.9.10、TypeScript 6.0.3、Vitest/coverage-v8 5.1.0、vue-tsc 3.3.14。npm ls --depth=0 正常。22 项直接依赖在 package.json、锁文件根声明、锁定版本和安装版本之间全部一致。未安装或更新前端依赖，锁文件未修改。

原有配置职责：eslint.config.js 负责 Vue/TS 静态检查；.prettierrc.json 负责格式；tsconfig.json 引用 app/node 两个严格检查项目；vitest.config.ts 复用 Vite、jsdom 和 Element Plus 转换配置。已有 lint、lint:fix、format、format:check、type-check、test、test:run、test:coverage、build。已解决早期类型检查不递归及 coverage provider 缺失的问题，无须再改。ESLint 通过，Prettier 首轮检出 8 个历史格式文件。实施前已向用户报告检查结论和文件计划。

## 2. 新增及修改文件

新增：pyproject.toml（Ruff/pytest 中文配置）、quality.py（根命令入口）、tests/conftest.py（测试环境隔离）、tests/unit/test_quality.py（失败传播及只读检查回归）、本记录。

修改：.gitignore（两种质量缓存）；frontend/package.json（新增 quality-check 并格式化该文件）；frontend/eslint.config.js（补充常见错误规则和中文说明）；app/main.py、app/core/config.py、exceptions.py、logging.py、middleware.py、tests/api/test_infrastructure.py、tests/unit/test_config.py（Ruff 格式、导入排序、移除测试未使用导入及等价 UTC 常量调整）。上述后端文件未整体覆盖或重写，未改变 API、校验、脱敏、中间件或异常行为。未修改前端 src、Element Plus 按需注册或业务逻辑。

AGENTS.md 原已完整包含中文配置要求，未重复追加、删除或改写规则。未增加应用配置项，Settings 字段与 .env.example 内容语义保持不变；不需要新增环境变量。

## 3. Ruff 规则

Python 目标 py311，行宽 100，双引号、空格缩进、LF。E4/E7/E9 检查导入及明显错误，F 检查未使用导入和名称错误，I 统一导入，B 检查常见陷阱，UP 检查现代 Python 写法，无额外忽略列表。中文长描述字符串保留原文，未启用将不可拆分字符串视作失败的 E501。

force-exclude 强制排除 docs/logs/scripts/data/frontend、虚拟环境、构建和缓存，避免根检查越界。Ruff 默认还排除标准版本控制和工具缓存。所有新选项均为非敏感工具设置，中文注释说明用途；无部署必填项。

## 4. ESLint 与 Prettier

沿用 Vue flat/recommended 与 TypeScript recommended、Vue SFC 解析器，TS 未使用变量由 @typescript-eslint/no-unused-vars 检查，避免基础规则重复误报。补充 no-unreachable、no-dupe-args，JS 补充 no-undef。Prettier 兼容配置仍位于最后，没有大面积关闭错误规则。

沿用 Prettier：2 空格、不用 Tab、单引号、不加分号、行宽 100、尾逗号 all、对象括号空格、箭头参数始终括号、LF；覆盖 Vue/TS/JSON 等支持文件。配置均非敏感、非必填开发默认值；tabWidth/printWidth 为正整数，useTabs/singleQuote/semi/bracketSpacing 为布尔值，其他枚举按上述固定值。format 写入，format:check 只检查。未添加忽略历史业务文件的规则。

## 5. pytest 与 Vitest

pytest 明确 tests 路径、test_*.py 文件、test_* 函数、Test* 类、异步 fixture function 作用域；保留 unit/api 目录。conftest 在应用收集前禁用真实 dotenv 并清除建模配置环境变量，预加载默认测试应用，随后恢复 Settings 路径定义；每个用例使用禁用真实 dotenv 的配置工厂，结束清除缓存，会话结束恢复宿主环境。临时 .env 配置测试继续显式传入合成文件，不依赖外部服务。首轮直接将类路径设为 None 导致旧路径断言失败（50 通过/1 失败），修正隔离方式后原断言及全部测试通过，未删除或削弱断言。

Vitest 保留 tests/ 与 src/ 中 test/spec 命名、jsdom、mock/env/global 恢复、Element Plus 转换及 V8 provider，不删除原 23 个用例。类型检查仍为 vue-tsc -b，两个项目 strict/noUnused 配置不变。

## 6. 统一入口与提交前方案

根目录使用 Python 3.11 环境执行：

```powershell
& 'D:/anaconda3/envs/feiyu/python.exe' quality.py backend lint
& 'D:/anaconda3/envs/feiyu/python.exe' quality.py backend format
& 'D:/anaconda3/envs/feiyu/python.exe' quality.py backend format-check
& 'D:/anaconda3/envs/feiyu/python.exe' quality.py backend test
& 'D:/anaconda3/envs/feiyu/python.exe' quality.py frontend test
& 'D:/anaconda3/envs/feiyu/python.exe' quality.py frontend quality-check
& 'D:/anaconda3/envs/feiyu/python.exe' quality.py all quality-check
```

目标可为 backend/frontend/all，命令支持 lint/format/format-check/test/quality-check。使用调用者 Python、PATH 中 npm，固定正确工作目录，失败立即返回原退出码。前端聚合 lint → format:check → type-check → test:run → build；后端聚合 lint → format-check → test。质量检查不执行 --fix/--write；类型检查缓存及构建产物按原规则忽略。两个新增测试验证失败停止及格式检查命令不写入。

Git 原状态、暂存、未暂存及未跟踪均为空。core.hooksPath 未设置，只有标准 sample hooks。暂不安装 hook 管理器、不修改 hooks/config/index、不自动提交。建议开发者提交前手工执行 all quality-check，修复失败并复查差异后自主暂存提交。检查失败不能绕过后声称通过。

## 7. 实际命令与最终结果

执行过版本/依赖核对、git status/diff、指定文件读取、pip 精确安装及以下验证；结果均来自本轮：

| 命令 | 最终结果 |
| --- | --- |
| Python 3.11 -m ruff check . | 通过 |
| Python 3.11 -m ruff format --check . | 21 个文件通过 |
| Python 3.11 -m pytest tests -q | 53 passed（原有 51、新增 2） |
| npm --prefix frontend run lint | 通过 |
| npm --prefix frontend run format:check | 失败，7 个历史文件 |
| npm --prefix frontend run type-check | 通过 |
| npm --prefix frontend run test:run | 4 文件、23 项通过 |
| npm --prefix frontend run build | 通过 |
| quality.py backend quality-check | 通过 |
| quality.py all quality-check | 正确返回 1，在前端格式检查处停止 |
| git diff --check | 通过（Git 有既有 LF/CRLF 转换提示） |

先运行 Ruff check，自动修复共 8 项诊断，再 format（8 文件格式变化），重新检查测试。前端仅对本次修改的 package.json、eslint.config.js 显式执行 Prettier --write。统一入口后续步骤被格式失败阻止，因此 type-check/test/build 另行实际执行，未将聚合失败解释为全绿。

## 8. 历史问题、保护检查与验收

最终 Prettier 未通过：frontend/index.html、package-lock.json、src/layouts/MainLayout.vue、src/main.ts、src/plugins/element-plus.ts、src/stores/modules/workspace.ts、tests/element-plus.test.ts。均在修改前已检出；package.json 原有格式问题已随本次修改修复。业务页面、状态文件及锁文件受保护，本次未批量格式化，也未新增 ignore 规避。待用户明确审核历史格式整理范围后再处理，当前完整验收标准未达到。

历史警告：Vitest 提示未来 native loader 对无扩展名配置导入的兼容问题；构建图表 chunk 超过 500 kB。未为隐藏警告改变配置或业务代码。原依赖清单和环境漂移已在第一节列出，不属本次新增。

后端配置、健康接口、日志/异常/并发隔离等原测试通过；前端真实按需组件及页面测试通过，依赖和锁文件保持原样。未进行浏览器/TCP 冒烟，不将自动化检查等同于完整人工业务验收。Git 索引保持空，无自动提交或配置修改。待人工审核后端纯格式差异、质量规则和前端历史格式处理范围。本次仅 P6-BASE-004，停止等待审核。

## 9. 补充整改：前端历史格式问题（2026-11-04）

### 9.1 范围与保护

本轮仅使用现有 Prettier 配置处理用户列明的 6 个文件、经单独确认转换锁文件换行，并在本记录末尾追加结果。保留本任务之前所有工作区修改和未跟踪交付；未修改后端代码、AGENTS.md、package.json、依赖版本、配置/日志/异常逻辑或其他文档。未安装依赖、重建锁文件、操作暂存区或自动提交。

### 9.2 六个文件结果与 diff 检查

在 frontend 目录显式执行现有工具：

```powershell
& ./node_modules/.bin/prettier.cmd --write index.html src/layouts/MainLayout.vue src/main.ts src/plugins/element-plus.ts src/stores/modules/workspace.ts tests/element-plus.test.ts
```

| 文件 | 纯格式调整 |
| --- | --- |
| index.html | 长 link 属性分行，title 单独成行，LF |
| src/layouts/MainLayout.vue | 长提示文案按 Prettier 规则换行，LF |
| src/main.ts | 仅 CRLF 转 LF |
| src/plugins/element-plus.ts | 仅 CRLF 转 LF，按需引入及注册完整保留 |
| src/stores/modules/workspace.ts | 仅 CRLF 转 LF |
| tests/element-plus.test.ts | 长断言和选择器换行，LF，测试用例未删除或简化 |

已检查上述路径完整 git diff：Git 规范化后仅 3 个文件有内容排版差异，合计 17 行增加、4 行删除；其余 3 个文件通过脚本与 HEAD 原文比较，确认仅换行变化。未改写业务表达式、导入列表或测试断言内容。

### 9.3 锁文件独立检查与用户确认

先通过现有 Prettier API 在内存生成预览，并将预览写入系统临时目录，未直接写入锁文件。检查结果：4,715 个 CRLF 需要转换为 LF，行数不变（4,715 个换行符）；171,864 字节变为 167,149 字节，减少 4,715 字节。解析后的 JSON 完全一致，Git 规范化后的内容差异为空。

因转换覆盖全文件，先暂停锁文件修改并报告规模与影响；用户明确回复“允许，仅转换锁文件换行”后，使用精确 CRLF→LF 替换写入，不重新生成锁文件、不执行依赖安装。写入前后均比较解析结果，并与 HEAD 字节内容比较，确认新内容严格等于原文仅替换 CRLF 的结果，依赖版本、依赖关系、完整性字段及其余内容均未变。

### 9.4 实际验证与最终结果

在 frontend 目录分别执行 npm run lint、npm run format:check、npm run type-check、npm run test:run、npm run build。锁文件确认前首轮 format:check 返回 1，仅剩 package-lock.json；其他四项均返回 0。锁文件转换后，在根目录执行：

```powershell
& 'D:/anaconda3/envs/feiyu/python.exe' quality.py all quality-check
```

使用已确认的 Python 3.11.18 环境，未使用系统默认 Python 3.13。统一入口实际依次执行后端三项和前端五项，完整运行退出码为 0：

| 实际命令 | 最终结果 |
| --- | --- |
| python -m ruff check . | 通过 |
| python -m ruff format --check . | 21 个文件通过 |
| python -m pytest tests -q | 53 passed，0.37s |
| npm run lint | 通过 |
| npm run format:check | 全部匹配文件通过 |
| npm run type-check | 通过 |
| npm run test:run | 4 个测试文件、23 项通过 |
| npm run build | 通过 |
| python quality.py all quality-check | 通过，退出码 0 |
| git diff --check | 通过 |

上述表中的 python 为 feiyu 环境解释器。最终前端五项通过来自统一入口的真实执行，不将锁文件转换前的格式失败计为通过。未重复新增测试或覆盖历史测试结果。

仍有原有非阻塞提示：Vitest 对未来 Vite native loader 无扩展名配置导入的提示、图表 chunk 超过 500 kB 的构建警告，以及 Git 的 LF/CRLF 自动转换提示；未通过关闭规则、提高阈值或修改 Git 配置隐藏提示。当前 Git 的换行转换策略在未来检出后可能重新产生 CRLF，本轮按保护要求未改用户 Git 配置。

### 9.5 验收结论

本轮格式阻塞已全部解除，前端格式检查和全项目统一质量入口通过，达到 BASE-004 自动化技术验收标准。Element Plus 按需引入及原有前后端测试继续通过，无本轮已知未解决失败项。待用户人工审核纯格式 diff、锁文件仅换行的处理及本补充记录；不将本次自动化验证等同于全部业务场景人工验收。本轮完成后停止，不开始 BASE-005。
