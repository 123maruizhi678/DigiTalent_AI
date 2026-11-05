# M1-GATE-R10 测试与验收报告

日期：2026-11-04（Asia/Shanghai）

## 1. 测试环境

- 工作区：D:\AI\DigiTalent_AI；Windows PowerShell。
- Conda 环境：feiyu；Python 3.11.18。
- Python：D:\anaconda3\envs\feiyu\python.exe。
- pip：26.2.2；模块目录 D:\anaconda3\envs\feiyu\Lib\site-packages\pip。
- pytest 入口：D:\anaconda3\envs\feiyu\Scripts\pytest.exe。
- 前端使用项目现有 Node/npm、Vitest、TypeScript、ESLint、Prettier 和 Vite；未安装、升级或替换依赖。Node/npm 具体版本在本次执行输出中未留存。

首次直接 conda activate 未使解释器离开 base，确认后未在该解释器执行开发或测试。随后初始化 PowerShell Conda hook 并重新激活，验证解释器、pip、pytest 均来自 feiyu 后执行后端检查。

## 2. 执行命令

环境确认：

```powershell
conda env list
(& conda 'shell.powershell' 'hook') | Out-String | Invoke-Expression
conda activate feiyu
python --version
python -c "import sys; print(sys.executable)"
python -m pip --version
Get-Command pytest | Select-Object -ExpandProperty Source
```

后端最终检查（项目根目录，激活 feiyu）：

```powershell
python -m ruff check app tests
python -m ruff format --check app tests
python -m pytest -q
```

前端最终检查（frontend 目录）：

```powershell
npm run quality-check
```

该脚本顺序执行 lint、format:check、type-check、test:run、build，分别对应 ESLint、Prettier、vue-tsc、Vitest 和生产构建。新增前端测试先使用项目现有 Prettier 格式化；Python 修改文件先使用项目现有 Ruff 格式化。

另外执行 `git diff --check -- . ':!docs'`，无差异空白错误；Git 有 LF/CRLF 转换提示。

## 3. 路径用例与验证层级

| 场景 | 预期最终 URL | 验证方式 |
| --- | --- | --- |
| 登录 | /api/v1/auth/login | 调用真实 authApi 模块，Axios Adapter 中 getUri；Vite 实际代理 |
| 刷新 | /api/v1/auth/refresh | 同上 |
| 退出 | /api/v1/auth/logout | 同上 |
| 当前用户 | /api/v1/auth/me | 同上 |
| 文件 | /api/v1/files | request 传输层拼接；Vite 实际代理 |
| Agent 执行 | /api/v1/agents/example/executions | request 传输层拼接；Vite 实际代理 |
| Workflow 执行 | /api/v1/workflows/example/executions | request 传输层拼接；Vite 实际代理 |

Axios 测试断言完整 URL 精确相等，覆盖重复前缀、遗漏版本及错误尾斜杠风险，并检查 withCredentials true。认证测试通过现有认证模块调用，不仅检查源码字符串。

Vite 测试读取现有代理配置，断言 `/api` target 与无 rewrite 的配置；启动真实 Vite 代理及临时 HTTP 上游，测试时仅将上游地址换为临时端口。逐一发起七类 HTTP 请求，断言上游收到完整路径，并检查响应 Set-Cookie 的 `/api/v1/auth` 路径未改写。此项不等同于真实后端业务联调，也未验证浏览器自动发送 Cookie。

后端测试验证实际 OpenAPI 业务路径只有 `/api/v1/health`；既有健康检查测试验证 HTTP 可访问性、重复前缀拒绝和方法限制。配置测试新增拒绝 `/api/test`、`/api`、`/api/api/v1`、`/api/v1/api/v1` 等非法值，保留既有缺少起始斜杠、尾斜杠校验。

Cookie 测试分别覆盖 development/production 属性模式，使用 httpx Cookie Jar 接收契约函数生成的 Cookie，验证认证路径携带、文件路径和相似路径不携带，以及清理后刷新请求不再携带。既有 R09 测试继续验证 HttpOnly、SameSite、Secure、host-only、有效期及 CSRF 等契约。

## 4. 最终测试结果

| 检查 | 结果 |
| --- | --- |
| Ruff check app tests | 通过 |
| Ruff format --check app tests | 22 个文件格式通过 |
| pytest -q | 76 项通过，0 失败 |
| ESLint | 通过 |
| Prettier | 通过 |
| TypeScript（vue-tsc -b） | 通过 |
| Vitest | 7 个测试文件、32 项测试通过，0 失败 |
| 前端生产 Build | 通过，2310 个模块完成转换 |

本次新增后端路径/Cookie 用例共 3 项；前端最终 URL 用例共 4 项、代理用例 1 项。完整回归覆盖原有配置、健康检查、基础设施、认证契约和前端测试。

## 5. 过程失败及修复

首次新增测试写入命令的工作目录与相对路径重复，目标不存在，未成功写入文件；随后改用明确绝对路径创建。

中间测试出现以下问题，均已修复后重新执行完整相关检查：

- TypeScript TS6307：应用测试直接导入不属于其 project 文件列表的 vite.config.ts；将代理验证独立为 Node 环境 JS 测试，未修改工程编译配置。
- 新增后端测试直接枚举 APIRoute 得到空列表；改用应用 OpenAPI 校验实际公开业务路径，保留既有真实 HTTP 健康检查测试。
- 新增 JS 测试 ESLint no-undef：fetch 未声明；改用 globalThis.fetch。

这些过程失败不作为最终通过结果；最终结果以上述重新执行的输出为准。

## 6. 警告及未执行项

- Vite 提示未来 native 配置加载对无扩展名导入的兼容性；当前执行通过，未扩大修改范围。
- 生产构建存在超过 500 kB 的分包提示；本次未进行无关构建优化。
- 未执行真实认证、文件、Agent、Workflow 后端端到端测试：相应真实路由尚未实现，不虚构接口可访问。
- 未执行真实生产反向代理及 HTTPS 浏览器联调：检查范围内未发现已有生产代理配置，未新增部署组件。
- 未执行真实浏览器认证 Cookie 生命周期验收；当前为契约函数、Cookie Jar 及代理响应头验证。

## 7. 遗留问题与人工验收

代码检查及自动化测试范围内无未解决路径冲突；R09 认证契约保持不变。生产部署需配置 `/api/` 转发并完整保留 `/api/v1`，核验实际 Cookie Path、HttpOnly、Secure、SameSite 以及设置、刷新、退出清理行为。后续真实 API 实现后补充业务集成测试，不属于本次开发范围。

## 8. 最终验收结论

最终状态：**部分完成**。

代码整改、七类路径验证和相关回归已通过；经用户后续明确授权，两份指定交付文档现已生成。生产部署验证仍待完成，因此不宣称完整生产环境验收通过。未开始 P6-IAM-004 或其他下一阶段任务，未提交 Git Commit。