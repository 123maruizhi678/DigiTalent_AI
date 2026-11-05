# M1-GATE-R10 API 路径统一决策与实施记录

日期：2026-11-04（Asia/Shanghai）

## 1. 范围与授权

本次仅处理 API 路径、代理一致性及对应测试。用户已明确授权在 `docs/开发日记/1104` 生成本记录和测试与验收报告；未扫描或修改其他文档。保留任务开始前已有未提交修改，未提交 Git Commit，未进入 P6-IAM-004、P6-IAM-005。

## 2. 原有路径问题

前端两个 Axios 实例默认均使用 `/api/v1`，认证 API 模块使用业务相对路径，Vite `/api` 代理没有 rewrite，默认组合正确。后端通过统一 Settings 的 API_V1_PREFIX 在应用入口挂载总 Router，但原配置允许任意合法路径，例如 `/api/test`；这会使后端与固定的前端前缀、R09 Cookie Path 不一致。两个 Axios 实例的公共配置重复定义，也存在后续修改漂移风险。

检查范围内未发现重复注册版本前缀。当前后端业务 API 仅有健康检查；认证为可复用契约代码，尚未注册真实认证路由。文件、Agent 执行、Workflow 执行的真实接口尚未实现。

## 3. 最终 API 路径规范

| 用途 | 方法及对外路径 |
| --- | --- |
| 登录 | POST /api/v1/auth/login |
| 刷新 | POST /api/v1/auth/refresh |
| 退出 | POST /api/v1/auth/logout |
| 当前用户 | GET /api/v1/auth/me |
| 文件路径 | /api/v1/files |
| Agent 执行路径 | /api/v1/agents/{agent_code}/executions |
| Workflow 执行路径 | /api/v1/workflows/{workflow_code}/executions |
| 已实现健康检查 | GET /api/v1/health |

上述规划路径不代表尚未实现的业务接口已经可访问。各环境统一使用 `/api/v1`，不允许遗漏 `/v1`、重复 `/api`、重复版本前缀或错误尾斜杠。

## 4. 后端路由约定

`app/main.py` 使用 `app.include_router(api_router, prefix=settings.API_V1_PREFIX)` 统一挂载；`app/api/router.py` 聚合子路由。子路由只定义业务路径。前缀字段改为 `Literal["/api/v1"]`，保留统一 Pydantic Settings 读取方式、默认值和非必填属性，非法前缀在配置校验时拒绝。

API_V1_PREFIX（API 版本前缀）为字符串，用于挂载总路由，默认且仅允许 `/api/v1`，非必填、非敏感。字段中文说明与 `.env.example` 已同步；未新增依赖、配置对象或凭据。

## 5. Axios 配置约定

`frontend/src/api/request.ts` 中公共 transportOptions 统一定义 baseURL `/api/v1`、timeout 15000、withCredentials true，分别创建 request 与 authTransport。保留两个实例，认证实例不安装资源请求的自动刷新拦截器，避免改变既有刷新行为。

API 模块只填写 `/auth/login`、`/auth/refresh`、`/auth/logout`、`/auth/me` 等业务路径，不重复填写版本前缀。现有 `auth.ts` 无需本次修改，任务开始前该文件的未提交工作已保留。

## 6. Vite 代理约定

保留现有 `frontend/vite.config.ts`：匹配 `/api`，target 为 `http://127.0.0.1:8080`，changeOrigin true，不配置 rewrite。浏览器通过前端同源地址访问 `/api/v1/...`，代理完整保留路径。实际代理测试通过临时上游验证七类路径以及响应 Set-Cookie Path 不变；测试未依赖真实业务 API。

## 7. 生产代理约定

检查范围内未发现已有生产反向代理配置，本次未新增 Nginx 或部署组件。生产部署必须转发 `/api/`，保留完整 `/api/v1/...` 路径，不通过 rewrite 删除或重复添加前缀，不改写 Cookie Path 至错误范围。认证 Cookie 应按 R09 保留属性，生产使用 HTTPS 和 Secure。

生产代理配置及实际部署联调尚待完成，不能认定已通过生产验证。

## 8. Cookie Path 与 R09

保持 Refresh Token 使用 HttpOnly Cookie，Path 固定 `/api/v1/auth`；前端 withCredentials true。登录、刷新、退出及当前用户路径均在该作用域内。设置与删除使用相同 Path；测试验证 Cookie 不发送到文件路径、相似名称 `/api/v1/authentication` 或错误前缀路径，退出清理后不再携带。

未修改 `app/common/auth_contract.py` 的 R09 契约，未开发真实登录、会话持久化或数据库业务。

## 9. 实际修改文件

| 文件 | 本次内容 |
| --- | --- |
| app/core/config.py | 固定版本前缀合法值，完善中文说明 |
| .env.example | 同步前缀说明及合法范围 |
| frontend/src/api/request.ts | 两个 Axios 实例复用公共配置 |
| tests/unit/test_config.py | 更新固定前缀测试，增加非法前缀覆盖；保留环境配置集成断言 |
| frontend/tests/api-paths.test.ts | 新增认证模块及业务相对路径的 Axios 最终 URL 测试 |
| frontend/tests/api-proxy.test.js | 新增 Vite 实际路径转发及响应 Cookie Path 测试 |
| tests/api/test_api_paths.py | 新增已注册 API 路径和 Cookie 作用域、删除测试 |

Vite 配置、后端 Router 入口无需修改。未覆盖用户既有认证代码、测试及其他未提交修改。

## 10. 后续开发约束

新增业务路由遵守统一挂载方式；新增前端 API 模块使用业务相对路径。禁止以调整 Cookie Path、修改 R09 契约或代理重写来规避路径不一致。真实业务 API 实现后需补充接口集成测试；生产部署后需人工核验实际请求 URL、Cookie 设置、刷新和退出行为。本次不自动开始下一阶段。