# P6-BASE-003：建立日志与异常基础设施

- 日期：2026-11-04（Asia/Shanghai）。
- 状态：实现和自动化验证完成，等待用户审核；不进入 BASE-004。

## 1. 原有实现与依据

实施前 Git 暂存、未暂存和未跟踪状态均为空。app/core 只有配置模块和包声明；无统一日志、请求追踪及自定义异常处理。main.py 已有 lifespan、统一配置读取和路由挂载；router.py 聚合健康路由。已有配置测试 31 项、健康 API 测试 2 项。

只读取用户明确指定的 M0、BASE-001、FE-001、BASE-002 四份依据文件及根 AGENTS.md，没有扫描 docs、logs、scripts、data。四份依据均存在。根 AGENTS.md 已包含完整中文配置规范，无需重复追加。

与 M0 的关系：沿用根目录 app 布局及统一错误结构，控制台输出、不实现安全审计或后续业务。请求路径采用路由模板，未知路由使用 <unmatched>，防止个人信息进入日志。未提供独立 API 错误码明细文件，未搜索替代文档；本阶段使用 AUTHENTICATION_ERROR、PERMISSION_ERROR、PARAMETER_ERROR、BUSINESS_ERROR、SYSTEM_ERROR 对应指定五类，具体后续业务码仍待 API 任务确认。

## 2. 新增与修改文件

新增：

- app/core/logging.py：统一日志初始化、JSON 格式、防御性脱敏、ContextVar。
- app/core/middleware.py：纯 ASGI 请求追踪及安全请求日志。
- app/core/exceptions.py：基础、参数、业务、权限、系统异常及全局转换。
- tests/api/test_infrastructure.py：18 项新增自动化测试（含参数化）。
- 本开发记录。

修改：app/main.py，仅增加三个模块导入、lifespan 日志初始化、异常处理器及中间件注册。保留原有生命周期结构、配置单例、唯一应用、路由和健康接口。

未修改 config.py、router.py、健康实现、原有测试、前端、环境模板、依赖文件或其他历史开发记录；没有操作 Git 索引。

## 3. 日志格式及配置

setup_logging 消费 get_settings() 已有 LOG_LEVEL、LOG_OUTPUT；默认 INFO 和 console，无新配置、无文件输出。自有控制台 handler 具有标记，重复调用复用；Uvicorn 日志转发至 root，关闭可能携带查询串的 access 日志。HTTPX/HTTPCore 使用 WARNING，避免 INFO 请求日志泄露完整 URL。

JSON 字段：time（UTC ISO 时间）、level、logger、message、request_id；请求日志另有 method、path（路由模板）、status_code、duration_ms。日志在 lifespan 启动时初始化，初始化失败直接阻止启动，不静默忽略。

已有外部 root handler 保留，不擅自删除测试或宿主的 handler；宿主自行配置的其他输出应自行遵守同等脱敏规范。

## 4. request_id

HTTP 头 X-Request-ID 只接受单个、1～64 字符的 ASCII 字母、数字、下划线或连字符；非法、重复或缺失时生成 req_ 加 UUID4 十六进制值。存放在 ContextVar 和 request.state.request_id，响应头统一覆盖为同一值。

纯 ASGI 中间件使用 token/reset 和嵌套 finally，在成功、异常、取消时恢复原上下文，兼容并发请求。未预期异常在用户中间件内转为安全 JSON，因此 DEBUG 模式也不会绕过安全处理。已经开始发送的流式响应无法改写为错误 JSON，此时记录受控诊断并继续抛出，由服务器结束连接；已有响应头仍携带 request_id。

## 5. 异常转换及示例

ApplicationError 的公开消息和字符串详情必须由调用方明确确认安全；参数、业务、权限、系统异常分别提供默认错误码及状态。SystemError 不接受原始消息。HTTPException 同时覆盖 FastAPI 与 Starlette（包括 404/405），保留状态及协议头，忽略可能敏感的原始 detail。

参数校验错误返回 422，仅公开参数来源（如 query/body）及固定中文提示，不返回输入、ctx、原始校验消息或用户控制的键。业务错误保留开发者指定的安全文案。未预期异常返回 500 和通用文案，日志只包含代码文件名、函数和行号，不记录异常原文、源码、绝对路径或局部变量。

示例：

```json
{"code":"SYSTEM_ERROR","message":"系统处理失败","data":{"errors":[]},"request_id":"req_示例标识"}
```

## 6. 敏感信息保护及边界

基础设施不采集请求体、查询串、Cookie、认证头、简历及配置对象；请求路径只保留模板。格式器只输出允许字段，忽略任意 extra。对常见键值凭据、URL 连接串、邮箱、长数字进行防御性遮盖；异常诊断不输出原始异常消息。

正则无法识别任意无标记的秘密或完整简历，业务调用方必须遵守禁止记录此类内容的契约。自定义异常公开消息和详情、HTTP 协议头必须由调用方提供安全值，不可直接传入原始业务数据或异常。

## 7. 依赖与验证

没有安装、升级或增加依赖，requirements.txt 未改。使用标准库及已有 FastAPI、Starlette、HTTPX、pytest。

执行：

```powershell
& 'D:\anaconda3\envs\feiyu\python.exe' -m pytest tests -q -p no:cacheprovider
```

首轮 49 passed；补充查询串保护和取消测试后，最终 **51 passed in 0.55s**（原有 33 项、新增 18 项）。覆盖日志配置及初始化幂等、JSON 字段与脱敏、合法/非法/重复 ID、日志与响应 ID 一致、12 个并发请求隔离、取消后恢复、五类异常/HTTP/参数验证、DEBUG 下未知异常脱敏、错误结构、健康检查及原配置回归。

健康原测试 2 项继续通过：HTTP 200、原 JSON 不变、OpenAPI 唯一 GET 注册、404/405 状态保留。此次为 TestClient lifespan 和 ASGI 测试，没有声明实际 TCP 或前端浏览器验证。

额外尝试 ruff 静态检查，当前 feiyu 解释器提示 No module named ruff，因此未执行成功；没有为此安装依赖或提前开展 BASE-004。git diff --check 通过，仅有原有换行转换提示。

测试只使用合成输入，新增测试禁用真实 .env，未读取或修改真实敏感配置。没有覆盖历史测试结果。

## 8. 验收与待人工检查

本阶段日志、请求追踪、统一异常、错误结构及原工程回归的自动化检查通过。待用户确认错误码命名及参数错误详情的最小公开粒度，并在实际部署日志采集环境验收输出；如未来引入流式响应，需单独验收响应开始后的失败行为。ruff 当前环境不可用为工具验证限制，不影响已完成的测试结果。

本次完成 P6-BASE-003，等待审核，不执行后续阶段。
