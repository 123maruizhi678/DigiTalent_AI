# M1-GATE-R09 API 接口契约

状态：契约确定，真实后端路由尚未实现；不得把组件测试视为业务验收。日期：2026-11-04。

## 统一传输约定

固定对外前缀 `/api/v1`；自定义部署前缀时须同步代理、前端及 Cookie Path。普通响应沿用现有工程：`code/message/data/request_id`，成功 code 为字符串 `0`。错误 data 为 `{ "errors": [] }`。所有认证响应 Cache-Control: no-store，不缓存个人信息。
Access Token 仅存在前端内存，通过 Authorization: Bearer <access_token> 访问资源。Refresh Token 只通过 Set-Cookie/Cookie，禁止出现在请求 JSON、响应 JSON、URL、浏览器存储或日志中。

| 接口 | 参数及Header | Cookie及认证 | CSRF | 成功 |
| --- | --- | --- | --- | --- |
| POST /api/v1/auth/login | application/json；account:string(1..254)、password:string(1..1024)，拒绝额外字段；Origin、X-CSRF-Protection: 1 | 不需要Bearer；不依赖旧Cookie | 必须 | 200，TokenData，设置新Cookie |
| POST /api/v1/auth/refresh | 空请求体；Origin、X-CSRF-Protection: 1 | 必须携带dt_refresh；不要求Bearer | 必须 | 200，TokenData，轮换Cookie |
| POST /api/v1/auth/logout | 空请求体；Origin、X-CSRF-Protection: 1 | Cookie识别当前会话；无需有效Bearer | 必须 | 200，data:null，清Cookie |
| GET /api/v1/auth/me | Authorization: Bearer <access_token> | 必须有效Access Token；不使用Refresh Cookie认证 | 不要求，GET无状态变更 | 200，CurrentUser |

## 登录接口

以现有账号进行密码哈希验证，不添加注册入口或固定演示账户。密码哈希算法及依赖由IAM任务落实，不在R09新增依赖。错误账号、密码错误、用户停用均返回401 AUTHENTICATION_ERROR，不泄露账号是否存在。登录创建新会话；若请求携带旧有效会话，撤销旧会话再建立新会话；事务失败不签发令牌。
TokenData：access_token:string、token_type固定Bearer、expires_in整数秒（上限900）、user:CurrentUser。密码和Refresh Token不可返回。
浏览器可能静默阻止Cookie，服务端不能宣称能探测Cookie已落地；刷新缺Cookie返回401并要求重新登录，禁止退回JSON传递Refresh Token。Cookie写入异常应撤销新会话并返回500，网络丢响应的孤立会话由到期清理处理。

## 刷新接口

校验Cookie摘要、会话期限、用户启用状态及撤销标记；事务锁定会话，原子消费旧记录、创建下一代并提交后返回新令牌。旧摘要保留至会话绝对到期用于重放识别。无效/缺失/过期/已撤销均401；检测已消费令牌时撤销整族会话，401并清Cookie，不给宽限期。并发同旧令牌一个可提交，后续触发整族撤销，已签发Access Token也随会话失效。此策略安全优先，客户端必须串行刷新。事务故障返回500，不签发未提交Cookie。

## 退出接口

先撤销当前会话并提交，再以相同名称、Path、Domain及安全属性清Cookie（Max-Age=0）。缺Cookie、无效Cookie、重复退出均200且清Cookie。撤销存储不可用返回500，不能声称已退出；前端仍立即清内存并提示服务端退出失败。已消费旧Cookie用于定位并撤销同族，旧Refresh不可继续使用。

## 当前用户接口

校验JWT签名、固定算法、iss/aud/sub/sid/iat/exp/jti以及服务端会话及用户启用状态。撤销或用户停用立即401，不等JWT到期。CurrentUser白名单：user_id:string、name:string、roles:string[]、permissions:string[]；不返回密码、哈希、Token或内部会话摘要。权限不足使用403 PERMISSION_ERROR，前端不可通过刷新解决403。

## 响应示例与状态码

登录/刷新成功（令牌为占位符，真实响应另有Set-Cookie）：
```json
{"code":"0","message":"success","data":{"access_token":"<access-token>","token_type":"Bearer","expires_in":900,"user":{"user_id":"u1","name":"用户","roles":[],"permissions":[]}},"request_id":"req_example"}
```
/me成功的data为上述user；退出成功的data为null。
```json
{"code":"AUTHENTICATION_ERROR","message":"认证失败或已失效","data":{"errors":[]},"request_id":"req_example"}
```
401：认证无效，Bearer资源同时带WWW-Authenticate: Bearer；403 CSRF_ERROR：CSRF校验失败；403 PERMISSION_ERROR：业务权限不足；422 PARAMETER_ERROR：参数错误（不回显输入）；429：登录限流；500 SYSTEM_ERROR：内部失败，固定安全文案。CSRF失败不得变更会话或清Cookie，避免跨站强制注销。登录限流由IAM实现，不在R09宣称可用。

## Cookie与部署

名称dt_refresh；HttpOnly=true；Path=/api/v1/auth；Domain省略（host-only）；SameSite=Lax；生产Secure=true，开发仅本机HTTP时false；Max-Age=604800（7日），不额外设置Expires。每次轮换Max-Age必须为绝对到期剩余秒数，不能延长7日绝对会话期限；组件默认值用于首次登录，刷新接入须传入剩余寿命。退出使用相同属性清理。
当前Vite /api代理到后端，浏览器侧同源；正式部署选择同源反向代理，实际生产拓扑尚待验收。不得直接开启跨站SameSite=None；如未来改为跨站部署，须重新评审Secure、CORS、第三方Cookie限制及CSRF。

## CSRF与前后端调用

登录/刷新/退出均要求浏览器自动发送的Origin与显式部署白名单精确匹配，拒绝null、缺失、近似域名；Referer不作为降级通道。再要求X-CSRF-Protection: 1自定义头，跨站无法通过普通表单携带。该头不是秘密Token，不声称使用双提交Token。SameSite是辅助措施。CORS默认不开放；将来如需跨源，仅精确允许可信Origin、凭据及必要Header，禁止反射Origin或通配。组件不从客户端Host推导可信Origin；IAM通过统一Settings提供白名单。
前端withCredentials=true，禁止读取HttpOnly Cookie；单实例Promise共享刷新；仅资源401 AUTHENTICATION_ERROR自动刷新一次并重放一次，认证接口和403不递归刷新；失败清内存。页面重载显式刷新恢复，/me不自动刷新。generation防旧响应覆盖新状态；退出等待在途刷新后提交注销。多标签页共享Cookie但当前未实现跨页锁：接入真实认证前必须以Web Locks串行化登录/刷新/退出，；不支持Web Locks时禁止自动恢复共享会话，提示使用受支持浏览器，未经评审不得降级为无锁多页刷新；不能声称当前支持多页并发。


## 审核整改：错误码与前端处理

| 场景 | HTTP状态 | 错误码 | 客户端处理 |
| --- | --- | --- | --- |
| CSRF校验失败 | 403 | CSRF_ERROR | 不刷新Token；提示请求来源或防护头异常 |
| 业务权限不足 | 403 | PERMISSION_ERROR | 不刷新Token；提示无权操作 |
| Token或会话失效 | 401 | AUTHENTICATION_ERROR | 非认证资源按一次刷新规则处理，失败重新登录 |

CSRF检查必须先于任何会话写入、轮换、撤销和Cookie操作。CSRF失败不得修改会话状态，不得清理用户Cookie，不返回Set-Cookie。权限检查在统一认证依赖通过后执行；前端按HTTP状态与业务错误码共同分支，不能把所有403当作登录过期。

错误响应保持统一结构，三个错误分别为：
```json
{"code":"CSRF_ERROR","message":"请求安全校验失败","data":{"errors":[]},"request_id":"req_example"}
```
```json
{"code":"PERMISSION_ERROR","message":"无权执行此操作","data":{"errors":[]},"request_id":"req_example"}
```
```json
{"code":"AUTHENTICATION_ERROR","message":"认证失败或已失效","data":{"errors":[]},"request_id":"req_example"}
```

## 审核整改：所有受保护API统一认证

P6-IAM-005：后端认证授权依赖的强制要求：所有受保护API（包括/auth/me及其他业务模块）必须复用同一认证依赖，先固定HS256验证JWT签名，拒绝none、其他算法及算法混淆，再验证iss、aud、sub、sid、iat、exp、jti，随后读取服务端会话。会话必须存在、未撤销、未过期且关联用户启用；sub必须与会话user_id一致。任一失败立即401 AUTHENTICATION_ERROR。不能仅在/auth/me检查会话，其他业务API不能仅凭签名放行。服务端会话存储故障返回500 SYSTEM_ERROR并拒绝访问，不伪装成有效会话。认证与业务权限职责分离，权限不足403 PERMISSION_ERROR，菜单隐藏不替代后端授权。

## 审核整改：JWT密钥与声明细则

签名密钥由部署者使用操作系统密码学随机源生成，至少32随机字节；开发、测试、生产均无默认值、无通用测试密钥，环境之间不共用。开发使用被Git忽略的本地.env；生产由受限Secret管理或运行环境注入，通过统一Pydantic Settings的SecretStr读取，不写仓库、日志、异常或响应。缺失/长度不足必须启动失败。此处仅定义契约，不新增实际变量。

密钥轮换：预先部署受控验证密钥集合，以kid标识当前签名密钥，kid仅在服务端白名单查找，禁止作为文件路径/URL。正常轮换先发布新验证密钥，再切签名，旧密钥仅验证最多900秒且不超过旧Token有效期，然后移除；未知kid拒绝。密钥泄露时立即移除受影响验证密钥、切换新密钥并撤销相关全部会话，所有实例同步后旧Token立即拒绝；同步期间隔离未更新实例，要求重新登录，不保留泄露密钥宽限。需要记录签名kid与会话关联供处置，不记录密钥本身。

| 声明 | 必填规则 |
| --- | --- |
| iss | 统一Settings配置的非空签发者字符串，所有环境显式配置，无推断值，精确匹配 |
| aud | 统一Settings配置的非空本服务受众字符串；本契约只接受单字符串精确匹配，不接受任意受众列表 |
| sub | 非空用户标识字符串，必须等于服务端会话user_id |
| sid | 非空会话标识字符串，对应session_id，不能由JWT自身证明会话有效 |
| iat | 整数UTC Unix秒，拒绝布尔/浮点；不得晚于当前时间，不得早于会话创建时间的整数秒 |
| exp | 整数UTC Unix秒，拒绝布尔/浮点；当前时间必须严格小于exp，0 < exp-iat <= 900，且不晚于会话expires_at |
| jti | 每次签发使用独立UUIDv4字符串；唯一约束/碰撞重生成，不复用同一jti |

统一使用UTC并保持服务器时钟同步；本契约时钟宽限为0秒。Access Token剩余寿命不得越过会话绝对期限，expires_in为实际剩余秒数，无正整数剩余寿命时401且不再签发。验证器必须显式要求全部声明，不能采用库的可选默认验证。

## 审核整改：Refresh编码、摘要与会话字段

以secrets.token_bytes(32)生成随机字节，Base64URL无填充编码为43个ASCII字符。服务端先验证字符集[A-Za-z0-9_-]和长度43，解码必须恰好32字节，重新编码必须等于输入以拒绝非规范尾位。refresh_token_hash为对原始32字节执行SHA-256得到的32字节摘要，数据库BINARY(32)存储，文档调试只能用合成样例，不输出真实摘要。比较使用常量时间比较。原始Refresh Token不得持久化（包括数据库、缓存、审计及备份），仅在签发/响应内存和浏览器HttpOnly Cookie短暂存在，不进入普通JSON响应体或日志；摘要不得作为客户端认证凭据，不能接受客户端直接提交摘要完成刷新。

| 字段 | 类型及用途 |
| --- | --- |
| session_id | UUID唯一主键，对应JWT sid |
| user_id | 用户外键，关联用户状态 |
| token_family_id | UUID会话族标识；同族生命周期和撤销边界 |
| refresh_token_hash | BINARY(32)，当前有效Refresh摘要，唯一索引 |
| token_generation | 非负整数，初始0，每次轮换加1 |
| created_at | UTC创建时间，登录事务确定 |
| expires_at | UTC绝对到期，created_at+604800秒，轮换不可修改 |
| revoked_at | UTC可空撤销时间，一旦撤销不得重新激活 |
| last_used_at | UTC最近成功使用时间，轮换事务更新 |
| status | active/revoked/expired，与到期和撤销字段保持一致；时间判定不可仅依赖异步状态更新 |

重放记录至少保存token_family_id、session_id、旧摘要、代次、consumed_at，摘要唯一；同族标识串联所有代次。保留至expires_at，清理任务仅删除当前时间>=expires_at的摘要及过期会话，清理延迟不延长认证有效期。未到期的已消费摘要不能提前删；事务中撤销族后保留记录至绝对过期，避免重放漏检。

## 审核整改：原子轮换与服务端并发

数据库操作顺序固定：
1. 开启事务；按当前/已消费摘要索引定位候选会话族，不对未知摘要创建记录。
2. 锁定对应会话族及当前会话行（SELECT FOR UPDATE），同族所有操作采用一致锁顺序；若需要锁用户，统一先锁用户再锁族/会话，撤销、登录、刷新使用同一顺序。
3. 锁内重新校验用户启用、会话存在、未撤销及未到期。
4. 校验当前Refresh摘要与代次；若命中已消费摘要，锁内标记整个会话族撤销并提交，返回401和清Cookie；未知摘要401，不撤销无关会话。
5. 原子消费旧Token：插入带唯一约束的旧摘要记录并以旧摘要/代次作CAS更新条件，受影响行数必须为1。
6. 生成新的32随机字节Refresh Token（数据库不保存原文）。
7. 保存下一代摘要、代次加1、last_used_at，expires_at保持不变。
8. 提交事务。唯一约束冲突、锁超时或事务失败必须回滚；失败响应不携带新令牌或Set-Cookie，不自动重跑整个刷新请求。
9. 提交成功后才返回新的Access Token及Set-Cookie；Access Token可在提交前准备，但不能提前发送。

CAS失败不得盲目覆盖，重新在锁内判断是否重放；并发同旧Token最多一个轮换提交，第二个识别重放后整族撤销，第一响应拿到的Access Token也因sid校验失效。无无条件宽限期，不将已消费Token解释为正常刷新。退出、停用和撤销同样使用上述锁边界，避免刷新与撤销互相覆盖。

## 审核整改：客户端并发、网络异常与恢复

单标签页多个业务401共用一个Promise；其他请求等待同一个结果，成功后均用新Access Token，原业务请求最多重试一次。迟到401若来自上一代Access Token，应复用已经更新的令牌，不额外轮换；刷新、登录、退出不经过资源401自动刷新拦截器。403不触发自动刷新，重放后仍401立即清内存并返回登录入口。

不采用安全幂等恢复机制：当前架构没有持久化加密响应恢复存储，且不能持久化原始Refresh，不增加Redis或缓存，也不通过返回旧结果弱化重放防护。刷新网络超时、断网、500或响应丢失均不自动重试刷新，不后台循环恢复；清除Access Token及用户/角色/权限状态、递增generation并进入“需重新登录”状态，阻止排队和新的资源请求继续触发刷新。迟到响应不得改变该状态。

服务器可能已提交轮换但客户端Cookie仍旧；再次使用旧Cookie必须视为重放，撤销整族并401，不视为正常网络重试。若Cookie已更新但响应体丢失，客户端同样不尝试静默恢复，仍重新登录。网络可用后，在同一认证互斥锁中尽力退出再重新登录；退出失败须提示未确认服务端注销，不能声称旧会话已撤销，但允许用户明确重新登录。登录携带当前或已消费旧Cookie时撤销可定位的旧会话族并新建会话；无法定位的孤立族不能凭空撤销，保留到绝对过期或由账号全会话撤销处置。

登录、刷新、退出统一采用generation保护，并通过同一串行队列协调。新登录先递增generation、清内存，等待旧刷新完成或超时，再在队列内尽力撤销旧会话后提交登录；退出先递增generation/清内存、等待在途刷新完成或超时，再发送退出。登录成功仅在generation未变化时写入状态；退出完成后迟到刷新响应不能恢复前端登录状态。超时的HTTP请求即使取消也不能保证浏览器不会处理迟到Set-Cookie；仍须禁止静默刷新、要求重新登录，依赖服务端撤销令旧Cookie不可用，绝不只用generation宣称解决Cookie竞态。

跨标签页必须使用同源Web Locks独占锁，固定名称digitalent-auth-session，锁覆盖登录/刷新/退出的完整网络请求和Cookie更新，不限于Promise创建。进入锁后重新检查认证版本和状态；用BroadcastChannel只传播版本、退出/需重新登录事件和重新校验指令，不传播任何Token。等待标签页获得锁后可串行刷新获取自己的内存令牌；该场景允许多次串行轮换，单标签内同批请求仍只刷新一次。不支持Web Locks的浏览器禁止自动共享会话恢复，需提示使用受支持浏览器或先评审替代机制。Web Locks、跨页广播和完整状态机本次未实现，继续列为前端接入前置验收项。

## 审核整改：配置及实施边界

P6-IAM-004/005及前端后续实现必须遵守上述契约。新增配置统一Pydantic Settings，每字段Field(description="中文说明")，配置类/分组/校验器中文注释，.env.example说明名称、用途、类型、默认值、必填、范围及敏感性；生产不设不安全默认值。敏感配置不进入Git或日志。本次只修订三份R09文件，不新增环境变量、依赖、Redis、数据库表或迁移，不提前开发IAM。已有组件不等于符合修订后全部契约，CSRF_ERROR映射、完整客户端状态机及统一认证依赖须在实际接入时落实并验证。

## 本轮整改验收结论

已完成（R09设计门禁）。本轮四项审核整改已纳入契约，文档契约检查10项通过。原运行时业务验收记录保留，不代表IAM业务已实现或通过；完整业务、跨标签页和生产验证仍由后续任务执行。本次只修改三份R09文档，未改正式设计或代码，未新增配置、依赖或迁移。
