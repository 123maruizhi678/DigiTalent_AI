# AI 数字化人才平台

# 04_API接口详细设计

-   文档编号：`2026_AI_TP_P5_04`
-   版本：`V1.0`
-   所属阶段：第五阶段------设计成果审查与开发实施准备
-   所属步骤：第04步------API接口详细设计
-   文档状态：五批确认完成，详细设计基线
-   确认范围：第1---30项，共五批
-   前置依据：第四阶段第07步《07_前后端API接口总体设计》、第五阶段第03步《03_数据库详细设计》及第四阶段后端、前端、AI工作流、安全权限设计成果

------------------------------------------------------------------------

## 1. 设计目标与范围

本文档把已经确认的API总体规范落实为可供FastAPI后端、Pydantic数据契约、OpenAPI文档和Vue
3前端联调使用的接口详细设计基线。

本文件明确：

1.  API统一规范、响应结构、分页、错误处理和幂等规则；
2.  JWT Bearer Token认证、邀请制账号激活、组织和数据范围授权；
3.  文件上传、元数据查询、下载、预览和删除；
4.  人才选拔、人才档案与画像、测评面试、Agent/Workflow、数字员工、任务调度和数据智能接口；
5.  异步任务状态、执行结果、取消、重试和轮询方式；
6.  主要请求字段、响应字段、权限、数据库关联、业务规则和事务边界；
7.  API测试、联调和验收标准。

### 1.1 业务范围

覆盖七大业务模块：

1.  人才选拔；
2.  人才档案与人才画像；
3.  智能测评与面试；
4.  AI Agent与工作流管理；
5.  数字员工与任务调度；
6.  数据智能与运营决策；
7.  用户、组织与权限管理。

当前不纳入：岗前培养与培训课程、企业知识库。

### 1.2 技术基线

  层次       技术                                       职责
  ---------- ------------------------------------------ --------------------------------------
  前端       Vue 3 + TypeScript                         页面、交互和类型消费
  前端路由   Vue Router                                 页面访问控制
  前端状态   Pinia                                      当前用户和全局状态
  前端请求   Axios                                      HTTP请求封装、Bearer Token和错误处理
  后端       FastAPI                                    API路由、依赖注入和OpenAPI
  数据契约   Pydantic                                   请求、响应和字段校验
  ORM        SQLAlchemy                                 MySQL数据访问
  迁移       Alembic                                    数据库结构迁移
  AI流程     LangChain + LangGraph                      Agent能力和多步骤Workflow
  文件解析   MinerU及格式适配器                         简历和文档解析
  任务调度   APScheduler + MySQL任务中心 + 独立Worker   调度和异步执行
  向量检索   Milvus                                     向量数据，不作为业务权威数据源

------------------------------------------------------------------------

## 2. 五批30项确认结果

### 2.1 第一批：API通用规范与数据契约

  ------------------------------------------------------------------------------------------------------------------------------------
  项目                    选择                    最终决定
  ----------------------- ----------------------- ------------------------------------------------------------------------------------
  1\. 接口详细设计粒度    A                       每个接口完整设计方法、路径、请求、响应、权限、错误、业务规则、数据库关联和事务边界

  2\. 请求Schema组织      B                       同一业务对象尽量复用Schema；按场景保留必要差异，不能因复用放宽校验或暴露敏感字段

  3\. 列表响应结构        A                       `items`、`total`、`page`、`page_size`

  4\. 分页默认值和最大值  A                       默认20条，最大100条；具体接口可以设置更严格上限

  5\. 错误响应结构        A                       统一响应结构，`data.errors`提供字段路径、错误类型和说明

  6\. 错误编码分类        B                       只采用认证、权限、参数、业务、系统五大类别
  ------------------------------------------------------------------------------------------------------------------------------------

### 2.2 第二批：认证、组织权限与文件接口

  ------------------------------------------------------------------------------------------------------------
  项目                    选择                    最终决定
  ----------------------- ----------------------- ------------------------------------------------------------
  7\. 认证凭据            B                       JWT Bearer Token，通过Authorization请求头携带

  8\. 登录标识            C                       用户名或邮箱使用同一个登录接口

  9\. 邀请和账号创建      A                       管理员创建账号，系统生成邀请链接，用户通过链接设置首次密码

  10\. 数据范围处理       A                       后端根据角色、组织关系和数据范围自动计算，前端不能扩大范围

  11\. 文件上传           A                       先上传创建文件资源，再使用文件ID关联业务对象

  12\. 文件下载和预览     A                       后端鉴权后返回文件流
  ------------------------------------------------------------------------------------------------------------

### 2.3 第三批：人才选拔、人才档案与画像

  ------------------------------------------------------------------------------------------------------
  项目                    选择                    最终决定
  ----------------------- ----------------------- ------------------------------------------------------
  13\.                    A                       分别建立独立资源接口
  项目、岗位、招聘需求                            

  14\. 候选人管理         A                       候选人采用独立资源接口

  15\. 简历上传与解析     A                       上传、解析触发、状态查询、结果获取分别设计

  16\. 简历解析执行       A                       异步执行，返回任务ID，HTTP轮询

  17\. 岗位与人才匹配     A                       单人匹配、批量匹配和结果查询；异步执行

  18\. 人才档案与画像     A                       分别建立资源接口；画像支持生成、查询、版本查看和审核
  ------------------------------------------------------------------------------------------------------

### 2.4 第四批：测评、面试与AI接口

  ----------------------------------------------------------------------------------------------------------------
  项目                    选择                    最终决定
  ----------------------- ----------------------- ----------------------------------------------------------------
  19\. 测评方案与题库     A                       分别建立独立资源接口，通过关联接口维护方案试题

  20\. 测评任务           A                       独立创建，异步执行，支持状态查询

  21\. 答题与评分         A                       答题提交、评分执行和评分结果查询分别设计；支持AI评分和人工复核

  22\. 测评报告           A                       报告生成、状态查询、详情获取和文件下载分别设计

  23\. 面试管理           A                       面试独立管理，覆盖安排、面试官、评价、结果和记录查询

  24\.                    A                       分别提供独立调用接口，统一异步执行、执行ID、状态查询和结果获取
  Agent与Workflow调用                             
  ----------------------------------------------------------------------------------------------------------------

### 2.5 第五批：数字员工、任务调度、数据智能与监控

  ----------------------------------------------------------------------------------------------------------------------
  项目                    选择                    最终决定
  ----------------------- ----------------------- ----------------------------------------------------------------------
  25\. 数字员工           A                       独立资源，支持创建、修改、查询、启停及Agent/Workflow关联

  26\. 任务中心           A                       统一任务接口，支持创建、查询、详情、分配、取消、重试和状态查询

  27\. 调度计划           A                       独立资源，支持创建、修改、启用、暂停、恢复、删除和执行记录查询

  28\. 数据智能           A                       指标定义、分析任务、分析结果、分析报告分别设计；耗时分析异步执行

  29\. 通知、导入导出     A                       提供独立业务接口；执行过程采用异步任务和结构化日志，不建立专用记录表

  30\. API监控            A                       提供健康检查、服务状态、接口统计和运行监控；敏感信息仅管理员可访问
  ----------------------------------------------------------------------------------------------------------------------

五批共30项全部确认完成，不需要第六批。

------------------------------------------------------------------------

## 3. API统一规范

### 3.1 前缀、命名和HTTP方法

统一前缀：

``` text
/api/v1/
```

资源使用小写英文复数名词。路径参数使用资源ID。

  HTTP方法   用途         约定
  ---------- ------------ --------------------------------------
  GET        查询         不改变业务资源
  POST       创建或提交   创建资源、提交任务、执行明确业务动作
  PUT        完整更新     完整替换资源
  PATCH      部分更新     只更新指定字段
  DELETE     删除         按业务规则删除或逻辑删除

示例：

``` http
GET    /api/v1/candidates
GET    /api/v1/candidates/{candidate_id}
POST   /api/v1/candidates
PATCH  /api/v1/candidates/{candidate_id}
DELETE /api/v1/candidates/{candidate_id}
```

业务动作使用明确的动作子资源，例如`/cancel`、`/retry`、`/activate`，并定义允许的状态前置条件。

### 3.2 统一成功响应

普通JSON API统一返回：

``` json
{
  "code": "0",
  "message": "success",
  "data": {},
  "request_id": "req_xxxxx"
}
```

  字段           类型                说明
  -------------- ------------------- -------------------------
  `code`         string              业务结果编码，成功为`0`
  `message`      string              结果说明
  `data`         object/array/null   业务数据
  `request_id`   string              当前请求追踪ID

文件下载等二进制响应不包装为JSON，但必须保留适当的HTTP响应头和可关联的请求追踪信息。

### 3.3 统一列表响应

``` json
{
  "code": "0",
  "message": "success",
  "data": {
    "items": [],
    "total": 0,
    "page": 1,
    "page_size": 20
  },
  "request_id": "req_xxxxx"
}
```

分页规则：

-   `page`从1开始，默认1；
-   `page_size`默认20，最大100；
-   特殊接口可以设置更低上限；
-   `sort_by`使用接口定义的白名单字段；
-   `sort_order`只允许`asc`或`desc`；
-   简单筛选使用Query Parameters；
-   复杂组合查询使用POST搜索接口。

### 3.4 统一错误响应

``` json
{
  "code": "VALIDATION_ERROR",
  "message": "请求参数验证失败",
  "data": {
    "errors": [
      {
        "field": "email",
        "type": "invalid_format",
        "message": "邮箱格式不正确"
      }
    ]
  },
  "request_id": "req_xxxxx"
}
```

字段级错误结构：

  字段        类型     说明
  ----------- -------- --------------------------------------
  `field`     string   字段路径，嵌套字段使用点号或数组索引
  `type`      string   稳定的错误类型
  `message`   string   面向用户的错误说明

### 3.5 五大错误类别

  -----------------------------------------------------------------------------------------------------------------------------------------------------------------------
  类别             典型编码                                                                                             HTTP状态码 说明
  ---------------- ----------------------------------------------------------------------------------------- --------------------- --------------------------------------
  认证错误         `AUTH_UNAUTHORIZED`、`AUTH_TOKEN_EXPIRED`                                                                   401 缺少、无效或过期认证凭据

  权限错误         `AUTH_FORBIDDEN`                                                                                            403 已认证但无权操作

  参数错误         `VALIDATION_ERROR`、`INVALID_PARAMETER`                                                                 422/400 参数格式、类型、范围或组合不符合要求

  业务错误         `BUSINESS_ERROR`、`RESOURCE_NOT_FOUND`、`RESOURCE_CONFLICT`、`INVALID_STATE_TRANSITION`             404/409/422 资源不存在、状态冲突或业务规则不满足

  系统错误         `INTERNAL_ERROR`、`DEPENDENCY_UNAVAILABLE`、`TIMEOUT`                                           500/502/503/504 服务内部或依赖组件异常
  -----------------------------------------------------------------------------------------------------------------------------------------------------------------------

错误编码必须稳定，不同业务含义不能复用同一编码。资源不存在归入本次确认的"业务错误"类别，不另增第六类。HTTP状态码必须真实表达处理结果，不使用HTTP
200掩盖认证、权限或服务器错误。

### 3.6 Schema复用原则

按照第2项确认，优先复用同一业务对象的字段组和基础Schema，但不能强行使用一个Schema覆盖所有场景。

建议模式：

-   `CandidateBase`：候选人共有字段；
-   `CandidateCreate`：创建请求；
-   `CandidateUpdate`：更新请求；
-   `CandidateResponse`：详情响应；
-   `CandidateListItem`：列表项响应。

复用约束：

1.  创建和更新的必填规则可以不同；
2.  更新Schema必须区分"未传字段"和"显式传null"；
3.  响应Schema不得包含密码哈希、令牌、内部密钥和无权限字段；
4.  列表项只返回页面所需字段，详情通过独立接口补充；
5.  嵌套关系使用独立响应Schema，避免无限递归和过度返回。

### 3.7 日期、媒体类型与参数校验

-   日期时间采用ISO 8601格式，后端统一存储UTC。
-   普通请求和响应使用`application/json`。
-   文件上传使用`multipart/form-data`。
-   文件下载使用二进制响应，媒体类型按文件内容确定。
-   Pydantic统一校验必填项、类型、长度、数值范围、枚举、日期、分页、文件和复杂查询结构。
-   前端校验仅用于改善体验，不能代替后端校验。

### 3.8 超时、幂等和重复请求

  接口类型         处理策略
  ---------------- --------------------------------
  普通查询         短时请求，避免不必要的长查询
  普通写入         按业务处理耗时设置超时
  文件上传         根据允许的文件大小设置上传超时
  AI及耗时任务     立即返回任务ID，后台执行
  Agent/Workflow   返回执行ID，异步查询状态

关键创建和提交操作支持`Idempotency-Key`请求头。后端按用户、接口和幂等键识别重复请求，并返回原操作结果或明确冲突。客户端请求超时不等于服务端执行失败；重试前应先查询原任务状态。

------------------------------------------------------------------------

## 4. 认证、邀请与权限接口

### 4.1 JWT Bearer Token

受保护接口统一携带：

``` http
Authorization: Bearer <access_token>
```

认证要求：

-   后端验证JWT签名、有效期、签发者和受众等必要声明；
-   Token中只放身份和授权判断所需的最小声明；
-   不把密码、密钥或个人敏感资料放入Token；
-   用户停用、角色变更和权限变更需要有明确的Token失效或权限刷新策略；
-   Access Token和Refresh
    Token的具体有效期、刷新轮换、多设备会话和撤销机制在安全实现评审中确定；
-   不在URL Query中传递Token。

本次确认了JWT Bearer
Token，但没有确认浏览器端Token存储方式和具体有效期，不在本文中虚构固定秒数。前端应评估内存保存、刷新凭据保护和XSS风险；Refresh
Token不得作为普通页面业务数据持久化。

### 4.2 认证接口

  方法   路径                         用途               权限
  ------ ---------------------------- ------------------ -------------------
  POST   `/api/v1/auth/login`         用户名或邮箱登录   公开，需限流
  POST   `/api/v1/auth/logout`        注销当前认证凭据   已登录
  POST   `/api/v1/auth/refresh`       刷新Access Token   有效Refresh Token
  GET    `/api/v1/auth/me`            获取当前用户信息   已登录
  GET    `/api/v1/auth/permissions`   获取当前用户权限   已登录
  GET    `/api/v1/auth/menus`         获取当前用户菜单   已登录

登录请求：

``` json
{
  "account": "username_or_email",
  "password": "user_password"
}
```

登录响应`data`：

``` json
{
  "access_token": "jwt_access_token",
  "refresh_token": "jwt_refresh_token",
  "token_type": "Bearer",
  "expires_in": 0,
  "user": {
    "id": "uuid",
    "username": "user01",
    "display_name": "用户",
    "status": "active"
  }
}
```

`expires_in`由服务端实际配置返回，不在API文档中固定时长。

### 4.3 邀请制账号接口

  ----------------------------------------------------------------------------------------------------
  方法              路径                                    用途                     权限
  ----------------- --------------------------------------- ------------------------ -----------------
  POST              `/api/v1/users`                         管理员创建待激活账号     用户管理权限

  POST              `/api/v1/users/{user_id}/invitations`   生成/重新发送邀请        用户管理权限

  POST              `/api/v1/auth/invitations/accept`       接受邀请并设置初始密码   邀请凭据

  GET               `/api/v1/auth/invitations/validate`     验证邀请链接有效性       持有邀请凭据
  ----------------------------------------------------------------------------------------------------

创建用户请求：

``` json
{
  "username": "new_user",
  "email": "user@example.com",
  "display_name": "新用户",
  "organization_ids": ["uuid"],
  "role_ids": ["uuid"]
}
```

接受邀请请求：

``` json
{
  "invitation_token": "one_time_secret",
  "new_password": "user_defined_password"
}
```

邀请规则：

1.  仅管理员可以创建账号和发起邀请；
2.  不开放公开注册；
3.  邀请凭据应随机生成、一次性使用、设置有效期；
4.  服务端只保存邀请凭据的哈希或等效安全校验材料；
5.  邀请成功后激活账号并使凭据失效；
6.  过期、已使用、已撤销的邀请不得再次激活；
7.  不在日志中记录明文邀请凭据。

数据库设计已决定不建立独立邀请记录表。当前邀请状态需要由`sys_user`上的必要状态字段承载，例如邀请凭据哈希、有效期和接受时间；这些字段属于实施字段评审项，不代表已完成建表。

### 4.4 用户、组织、角色和权限接口

  --------------------------------------------------------------------------------------------------------------------
  方法               路径                                                用途                 权限
  ------------------ --------------------------------------------------- -------------------- ------------------------
  GET/POST           `/api/v1/users`                                     用户列表/创建        用户管理

  GET/PATCH          `/api/v1/users/{user_id}`                           用户详情/修改        用户管理或本人受限修改

  POST               `/api/v1/users/{user_id}/activate`                  启用用户             用户管理

  POST               `/api/v1/users/{user_id}/deactivate`                停用用户             用户管理

  GET/POST           `/api/v1/organizations`                             组织列表/创建        组织管理

  GET/PATCH          `/api/v1/organizations/{organization_id}`           组织详情/修改        组织管理

  GET                `/api/v1/organizations/{organization_id}/members`   组织成员             组织数据权限

  GET/POST           `/api/v1/roles`                                     角色列表/创建        角色管理

  GET/PATCH/DELETE   `/api/v1/roles/{role_id}`                           角色详情/修改/删除   角色管理

  GET                `/api/v1/permissions`                               权限定义列表         权限管理

  PUT                `/api/v1/roles/{role_id}/permissions`               设置角色权限集合     权限管理

  PUT                `/api/v1/users/{user_id}/roles`                     设置用户角色集合     用户授权

  GET                `/api/v1/users/{user_id}/organizations`             查询用户组织关系     用户/组织管理

  PUT                `/api/v1/users/{user_id}/organizations`             设置用户组织关系     用户/组织管理
  --------------------------------------------------------------------------------------------------------------------

权限响应示例：

``` json
{
  "items": [
    {
      "permission_code": "candidate.read",
      "resource_type": "candidate",
      "action": "read"
    }
  ]
}
```

### 4.5 数据范围授权

数据范围由后端自动计算。前端不能通过传入其他`organization_id`扩大查询范围。

后端授权顺序：

1.  验证Token及用户状态；
2.  读取用户角色和权限；
3.  计算用户组织关系及数据范围；
4.  将数据范围约束应用于数据库查询；
5.  对单条资源执行相同的资源级权限校验；
6.  对文件下载和AI工具调用再次校验业务对象权限。

典型数据范围：本人、所属组织、组织及下级组织、授权范围、全部数据。最终范围枚举和显式拒绝优先级应与权限详细设计一致。

------------------------------------------------------------------------

## 5. 统一文件资源接口

### 5.1 接口清单

  方法     路径                                 用途
  -------- ------------------------------------ ------------------------
  POST     `/api/v1/files`                      上传文件并创建文件资源
  GET      `/api/v1/files/{file_id}`            查询文件元数据
  GET      `/api/v1/files/{file_id}/download`   下载文件流
  GET      `/api/v1/files/{file_id}/preview`    文件预览
  DELETE   `/api/v1/files/{file_id}`            删除文件资源
  POST     `/api/v1/file-links`                 将文件关联到业务对象
  DELETE   `/api/v1/file-links/{link_id}`       解除业务关联

上传使用`multipart/form-data`，字段：

  字段            类型       必填 说明
  --------------- -------- ------ --------------
  `file`          binary       是 文件内容
  `category`      string       是 文件用途类别
  `description`   string       否 文件说明

上传成功响应`data`：

``` json
{
  "file_id": "uuid",
  "file_name": "resume.pdf",
  "file_type": "application/pdf",
  "file_size": 102400,
  "content_hash": "sha256:...",
  "status": "available"
}
```

关联文件请求：

``` json
{
  "file_id": "uuid",
  "owner_type": "candidate_resume",
  "owner_id": "uuid",
  "relation_type": "source_resume"
}
```

文件接口规则：

-   先上传创建文件资源，再通过文件ID关联业务对象；
-   MySQL保存`common_file`元数据，文件本体存首期本地文件系统；
-   后端验证文件大小、扩展名、实际内容和MIME类型；
-   使用安全生成文件名，原始文件名仅作为元数据；
-   下载和预览必须检查当前用户对文件及其业务对象的访问权限；
-   删除前检查业务引用；被业务对象引用的文件不得直接物理删除；
-   下载返回二进制流和适当的`Content-Type`、`Content-Disposition`；
-   预览只允许支持且经过安全处理的文件类型；
-   服务器内部绝对路径不得返回给前端。

------------------------------------------------------------------------

## 6. 人才选拔模块接口

### 6.1 项目与项目群

  ------------------------------------------------------------------------------------------------------
  方法                    路径                                              用途
  ----------------------- ------------------------------------------------- ----------------------------
  GET/POST                `/api/v1/project-groups`                          项目群列表/创建

  GET/PATCH/DELETE        `/api/v1/project-groups/{group_id}`               项目群详情/修改/归档或删除

  GET/POST                `/api/v1/projects`                                项目列表/创建

  GET/PATCH               `/api/v1/projects/{project_id}`                   项目详情/修改

  GET/POST                `/api/v1/project-requirements`                    项目需求列表/创建

  GET/PATCH               `/api/v1/project-requirements/{requirement_id}`   需求详情/修改
  ------------------------------------------------------------------------------------------------------

项目创建请求主要字段：

``` json
{
  "project_group_id": "uuid",
  "name": "AI人才招聘项目",
  "owner_id": "uuid",
  "description": "项目说明",
  "status": "draft"
}
```

项目需求创建请求：

``` json
{
  "project_id": "uuid",
  "requirement_name": "算法工程师招聘需求",
  "description": "需求说明",
  "priority": "high"
}
```

### 6.2 岗位与招聘需求

  -----------------------------------------------------------------------------------------
  方法                    路径                                      用途
  ----------------------- ----------------------------------------- -----------------------
  GET/POST                `/api/v1/positions`                       岗位列表/创建

  GET/PATCH               `/api/v1/positions/{position_id}`         岗位详情/修改

  GET/POST                `/api/v1/recruitments`                    招聘需求列表/创建

  GET/PATCH               `/api/v1/recruitments/{recruitment_id}`   招聘需求详情/修改

  POST                    `/api/v1/recruitments/search`             复杂招聘需求查询
  -----------------------------------------------------------------------------------------

岗位创建主要字段：

``` json
{
  "position_code": "AI-ENG-001",
  "name": "AI应用工程师",
  "job_family": "AI",
  "description": "岗位职责",
  "requirements": {
    "skills": ["Python", "LangGraph"],
    "experience_level": "experienced"
  }
}
```

招聘需求创建主要字段：

``` json
{
  "project_requirement_id": "uuid",
  "position_id": "uuid",
  "headcount": 2,
  "start_date": "2026-11-03",
  "end_date": "2026-12-03"
}
```

### 6.3 候选人管理

  方法       路径                                             用途
  ---------- ------------------------------------------------ -----------------
  GET/POST   `/api/v1/candidates`                             候选人列表/创建
  POST       `/api/v1/candidates/search`                      复杂条件搜索
  GET        `/api/v1/candidates/{candidate_id}`              候选人详情
  PATCH      `/api/v1/candidates/{candidate_id}`              修改候选人信息
  POST       `/api/v1/candidates/{candidate_id}/archive`      归档候选人
  GET        `/api/v1/candidates/{candidate_id}/resumes`      查询候选人简历
  GET        `/api/v1/candidates/{candidate_id}/selections`   查询选拔记录

创建候选人主要字段：

``` json
{
  "name": "候选人姓名",
  "phone": "手机号",
  "email": "candidate@example.com",
  "source": "referral"
}
```

人才主档案与候选人主体已确认合并。候选人API是人才主体在招聘选拔场景下的业务视图，必须映射到统一人才主体ID；不得因`/candidates`和`/talents`路径不同而创建重复自然人主档案。候选人选拔流程记录仍然独立管理。

### 6.4 简历上传、解析与结果

  方法   路径                                          用途
  ------ --------------------------------------------- ------------------------
  POST   `/api/v1/resumes`                             创建简历资源并关联文件
  GET    `/api/v1/resumes/{resume_id}`                 查询简历元数据
  POST   `/api/v1/resume-parses`                       提交简历解析任务
  GET    `/api/v1/resume-parses/{task_id}`             查询解析任务状态
  GET    `/api/v1/resume-parses/{task_id}/result`      获取解析结果
  GET    `/api/v1/candidates/{candidate_id}/resumes`   查询候选人简历

简历资源创建请求：

``` json
{
  "candidate_id": "uuid",
  "file_id": "uuid",
  "resume_type": "original"
}
```

解析任务请求：

``` json
{
  "resume_id": "uuid",
  "parse_options": {
    "extract_tables": true,
    "extract_images": true
  }
}
```

解析任务响应：

``` json
{
  "task_id": "uuid",
  "status": "pending",
  "submitted_at": "2026-11-03T10:00:00Z"
}
```

解析结果响应主要结构：

``` json
{
  "resume_id": "uuid",
  "parse_status": "succeeded",
  "parsed_at": "2026-11-03T10:02:00Z",
  "result": {
    "basic_information": {},
    "education": [],
    "work_experience": [],
    "projects": [],
    "skills": []
  }
}
```

解析约束：

-   MinerU及专用解析器在后台执行；
-   提交接口不等待完整解析；
-   返回任务ID，前端HTTP轮询；
-   MySQL简历记录只保留最新解析结果；
-   解析过程和异常细节进入结构化日志；
-   不覆盖原始简历文件；
-   AI抽取结果不能未经业务确认直接覆盖人才正式档案。

### 6.5 简历智能筛选

  ------------------------------------------------------------------------------------------------
  方法                    路径                                             用途
  ----------------------- ------------------------------------------------ -----------------------
  POST                    `/api/v1/screening-tasks`                        创建筛选任务

  GET                     `/api/v1/screening-tasks/{task_id}`              查询筛选任务状态

  GET                     `/api/v1/screening-tasks/{task_id}/result`       获取筛选结果

  POST                    `/api/v1/screening-results/{result_id}/review`   人工复核筛选结果
  ------------------------------------------------------------------------------------------------

创建请求：

``` json
{
  "recruitment_id": "uuid",
  "candidate_ids": ["uuid"],
  "screening_criteria": {
    "required_skills": ["Python"],
    "experience_level": "experienced"
  }
}
```

筛选结果至少包括候选人ID、结果等级、匹配依据摘要、未满足条件、模型/规则版本、生成时间和人工复核状态。筛选结果是辅助决策，不自动等同于最终淘汰或录用结论。

### 6.6 岗位与人才匹配

  方法   路径                                         用途
  ------ -------------------------------------------- ------------------
  POST   `/api/v1/matches`                            创建单人匹配任务
  POST   `/api/v1/matches/batch`                      创建批量匹配任务
  GET    `/api/v1/matches/{task_id}`                  查询匹配任务状态
  GET    `/api/v1/matches/{task_id}/results`          查询匹配结果
  GET    `/api/v1/match-results/{result_id}`          查询单条匹配详情
  POST   `/api/v1/match-results/{result_id}/review`   人工复核匹配结果

单人匹配请求：

``` json
{
  "candidate_id": "uuid",
  "position_id": "uuid",
  "recruitment_id": "uuid"
}
```

批量匹配请求：

``` json
{
  "recruitment_id": "uuid",
  "candidate_ids": ["uuid-1", "uuid-2"]
}
```

匹配结果包括分数、匹配等级、技能匹配、经历匹配、差距分析、解释摘要和模型/规则版本。匹配异步执行，使用任务ID轮询。匹配分数不能代替正式选拔结论。

### 6.7 选拔记录

  方法    路径                                      用途
  ------- ----------------------------------------- --------------------
  GET     `/api/v1/selection-records`               选拔记录列表
  POST    `/api/v1/selection-records`               创建选拔记录
  GET     `/api/v1/selection-records/{record_id}`   选拔详情
  PATCH   `/api/v1/selection-records/{record_id}`   更新选拔阶段或结果

关联数据库：项目、项目需求、岗位、招聘需求、统一人才主体、简历、匹配结果和选拔记录等表。写入选拔记录时校验候选人、招聘需求和操作者的数据范围。

------------------------------------------------------------------------

## 7. 人才档案与画像模块接口

### 7.1 人才主档案

  方法    路径                             用途
  ------- -------------------------------- ------------------
  GET     `/api/v1/talents`                人才列表
  POST    `/api/v1/talents/search`         复杂人才搜索
  GET     `/api/v1/talents/{talent_id}`    人才详情
  PATCH   `/api/v1/talents/{talent_id}`    修改人才主档案
  POST    `/api/v1/talents/merge`          提交人才档案合并
  GET     `/api/v1/talent-merge-records`   查询合并记录

人才详情返回主体信息和必要汇总，不默认无限嵌套经历、技能、标签、画像和全部历史记录。关联信息通过独立接口查询。

### 7.2 经历、技能和标签

  ----------------------------------------------------------------------------------------------
  方法                    路径                                           用途
  ----------------------- ---------------------------------------------- -----------------------
  GET/POST                `/api/v1/talents/{talent_id}/experiences`      经历列表/新增

  PATCH/DELETE            `/api/v1/talent-experiences/{experience_id}`   经历修改/删除

  GET                     `/api/v1/skills`                               技能字典

  GET                     `/api/v1/talents/{talent_id}/skills`           人才技能

  PUT                     `/api/v1/talents/{talent_id}/skills`           更新人才技能集合

  GET                     `/api/v1/tags`                                 标签字典

  GET                     `/api/v1/talents/{talent_id}/tags`             人才标签

  PUT                     `/api/v1/talents/{talent_id}/tags`             更新人才标签集合
  ----------------------------------------------------------------------------------------------

经历请求：

``` json
{
  "experience_type": "WORK",
  "organization_name": "示例公司",
  "title": "AI工程师",
  "start_date": "2023-01-01",
  "end_date": "2025-01-01",
  "description": "工作内容"
}
```

`experience_type`按数据库设计使用`EDUCATION`、`WORK`、`PROJECT`。技能和标签使用字典ID关联，不由前端自由创建未经校验的字典项。

### 7.3 员工身份

  -------------------------------------------------------------------------------------------------
  方法                    路径                                              用途
  ----------------------- ------------------------------------------------- -----------------------
  GET                     `/api/v1/talents/{talent_id}/employee-identity`   查询员工身份

  PUT                     `/api/v1/talents/{talent_id}/employee-identity`   建立或更新员工身份

  PATCH                   `/api/v1/employee-identities/{identity_id}`       更新任职信息
  -------------------------------------------------------------------------------------------------

员工身份独立于人才主档案，使用统一人才ID关联。员工编号和组织关系必须校验唯一性及管理权限。

### 7.4 人才画像

  ---------------------------------------------------------------------------------------------------------
  方法                    路径                                                     用途
  ----------------------- -------------------------------------------------------- ------------------------
  GET                     `/api/v1/talents/{talent_id}/profile`                    查询当前画像

  POST                    `/api/v1/talents/{talent_id}/profile-generations`        提交画像生成任务

  GET                     `/api/v1/profile-generations/{task_id}`                  查询画像生成状态

  GET                     `/api/v1/talent-profiles/{profile_id}/versions`          查询画像版本

  GET                     `/api/v1/talent-profile-versions/{version_id}`           查询指定版本

  POST                    `/api/v1/talent-profile-versions/{version_id}/reviews`   提交画像审核

  POST                    `/api/v1/talent-profile-versions/{version_id}/publish`   发布审核通过的画像版本
  ---------------------------------------------------------------------------------------------------------

画像生成请求：

``` json
{
  "source_scope": {
    "include_experiences": true,
    "include_skills": true,
    "include_assessments": true
  },
  "generation_options": {
    "language": "zh-CN"
  }
}
```

画像生成异步执行，响应任务ID。画像版本需记录来源、生成时间、模型/Prompt版本。AI画像不直接覆盖人才原始档案；正式发布前按权限执行人工审核。

关联数据库：人才主档案、经历、技能、标签、画像、画像版本、审核和变更记录。

------------------------------------------------------------------------

## 8. 智能测评与面试模块接口

### 8.1 测评方案

  -------------------------------------------------------------------------------------------------
  方法                    路径                                              用途
  ----------------------- ------------------------------------------------- -----------------------
  GET/POST                `/api/v1/assessment-plans`                        方案列表/创建

  GET/PATCH               `/api/v1/assessment-plans/{plan_id}`              方案详情/修改

  POST                    `/api/v1/assessment-plans/{plan_id}/activate`     启用方案

  POST                    `/api/v1/assessment-plans/{plan_id}/deactivate`   停用方案

  GET                     `/api/v1/assessment-plans/{plan_id}/questions`    查询方案试题

  PUT                     `/api/v1/assessment-plans/{plan_id}/questions`    设置方案试题关联
  -------------------------------------------------------------------------------------------------

方案创建请求：

``` json
{
  "name": "后端工程师综合测评",
  "assessment_type": "technical",
  "description": "测评说明",
  "plan_config": {
    "duration_minutes": 60,
    "total_score": 100
  }
}
```

方案只保存最新配置，不建立独立方案版本表。每次创建测评任务时必须保存实际使用的`plan_snapshot`，保证历史任务可还原。

### 8.2 题库与试题

  ----------------------------------------------------------------------------------------------
  方法                    路径                                           用途
  ----------------------- ---------------------------------------------- -----------------------
  GET/POST                `/api/v1/assessment-questions`                 试题列表/创建

  GET/PATCH/DELETE        `/api/v1/assessment-questions/{question_id}`   试题详情/修改/停用

  POST                    `/api/v1/assessment-questions/search`          复杂试题筛选
  ----------------------------------------------------------------------------------------------

试题请求主要字段：

``` json
{
  "question_code": "JAVA-001",
  "question_type": "single_choice",
  "content": "题目内容",
  "options": [],
  "standard_answer": {},
  "scoring_rule": {}
}
```

题库与试题采用统一表，通过`question_type`区分题型。不同题型的`options`、答案和评分规则由Pydantic按类型校验。不建立独立试卷表。

### 8.3 测评任务

  方法   路径                                          用途
  ------ --------------------------------------------- --------------------
  POST   `/api/v1/assessment-tasks`                    创建测评任务
  GET    `/api/v1/assessment-tasks`                    测评任务列表
  GET    `/api/v1/assessment-tasks/{task_id}`          测评任务详情和状态
  POST   `/api/v1/assessment-tasks/{task_id}/start`    启动测评
  POST   `/api/v1/assessment-tasks/{task_id}/cancel`   取消测评

创建请求：

``` json
{
  "candidate_id": "uuid",
  "plan_id": "uuid",
  "scheduled_at": "2026-11-04T02:00:00Z"
}
```

创建任务时校验候选人、方案状态、操作权限和时间条件；保存方案快照。测评任务与任务执行过程分别管理。

### 8.4 答题提交和评分

  ------------------------------------------------------------------------------------------------------
  方法                    路径                                                   用途
  ----------------------- ------------------------------------------------------ -----------------------
  POST                    `/api/v1/assessment-tasks/{task_id}/responses`         提交答题

  GET                     `/api/v1/assessment-tasks/{task_id}/responses`         查询答题记录

  POST                    `/api/v1/assessment-tasks/{task_id}/scoring`           提交评分任务

  GET                     `/api/v1/assessment-tasks/{task_id}/scoring`           查询评分结果

  POST                    `/api/v1/assessment-responses/{response_id}/reviews`   人工复核评分
  ------------------------------------------------------------------------------------------------------

答题请求：

``` json
{
  "question_id": "uuid",
  "answer_content": {
    "selected_option": "B"
  },
  "submitted_at": "2026-11-04T03:00:00Z"
}
```

评分执行可以异步完成。答题原始内容、AI评分、人工复核状态和正式结论需要区分；评分结果不能未经复核自动成为录用决定。

### 8.5 测评报告

  ---------------------------------------------------------------------------------------------------
  方法                    路径                                                用途
  ----------------------- --------------------------------------------------- -----------------------
  POST                    `/api/v1/assessment-tasks/{task_id}/reports`        提交报告生成

  GET                     `/api/v1/assessment-reports/{report_id}`            报告详情

  GET                     `/api/v1/assessment-reports/{report_id}/status`     报告生成状态

  GET                     `/api/v1/assessment-reports/{report_id}/download`   报告文件下载
  ---------------------------------------------------------------------------------------------------

报告生成响应返回任务ID或报告ID及状态。报告文件放文件系统，MySQL保存报告元数据和文件引用。

### 8.6 面试安排与评价

  --------------------------------------------------------------------------------------------------
  方法                    路径                                               用途
  ----------------------- -------------------------------------------------- -----------------------
  GET/POST                `/api/v1/interviews`                               面试列表/创建

  GET/PATCH               `/api/v1/interviews/{interview_id}`                面试详情/修改

  POST                    `/api/v1/interviews/{interview_id}/schedule`       安排面试时间

  PUT                     `/api/v1/interviews/{interview_id}/interviewers`   设置面试官

  POST                    `/api/v1/interviews/{interview_id}/evaluations`    提交面试评价

  GET                     `/api/v1/interviews/{interview_id}/evaluations`    查询面试评价

  POST                    `/api/v1/interviews/{interview_id}/analysis`       提交面试AI分析

  GET                     `/api/v1/interviews/{interview_id}/analysis`       查询分析结果
  --------------------------------------------------------------------------------------------------

面试独立于测评任务管理，可以关联测评任务，但面试材料、测评答题和AI分析结果必须保持来源区分。AI分析属于辅助信息，正式面试结论由有权限的人员确认。

------------------------------------------------------------------------

## 9. Agent与Workflow接口

### 9.1 定义查询接口

Agent、Prompt、Tool和Workflow定义使用代码及配置文件管理，不建立MySQL配置表。API只提供受控的定义查询和运行能力，不提供直接写配置文件的通用接口。

  方法   路径                                  用途
  ------ ------------------------------------- --------------------
  GET    `/api/v1/agents`                      查询已注册Agent
  GET    `/api/v1/agents/{agent_code}`         查询Agent元信息
  GET    `/api/v1/tools`                       查询可用Tool元信息
  GET    `/api/v1/workflows`                   查询已注册Workflow
  GET    `/api/v1/workflows/{workflow_code}`   查询Workflow元信息

定义查询结果只暴露前端需要且允许公开的名称、用途、版本和能力说明，不返回内部Prompt秘密、工具凭据或服务配置。

### 9.2 Agent执行

  --------------------------------------------------------------------------------------------------
  方法                    路径                                               用途
  ----------------------- -------------------------------------------------- -----------------------
  POST                    `/api/v1/agents/{agent_code}/executions`           提交Agent执行

  GET                     `/api/v1/agent-executions/{execution_id}`          查询执行状态和摘要

  GET                     `/api/v1/agent-executions/{execution_id}/result`   获取执行结果

  POST                    `/api/v1/agent-executions/{execution_id}/cancel`   取消执行
  --------------------------------------------------------------------------------------------------

请求：

``` json
{
  "business_type": "candidate",
  "business_id": "uuid",
  "input": {},
  "options": {}
}
```

响应：

``` json
{
  "execution_id": "uuid",
  "status": "pending",
  "agent_code": "resume_screening_agent",
  "agent_version": "1.0"
}
```

执行记录在MySQL保存摘要、状态、版本和关联ID；详细模型调用和Tool过程进入结构化日志。调用前必须校验当前用户对业务对象和Agent能力的权限。

### 9.3 Workflow执行与Checkpoint控制

  ---------------------------------------------------------------------------------------------------------
  方法                    路径                                                      用途
  ----------------------- --------------------------------------------------------- -----------------------
  POST                    `/api/v1/workflows/{workflow_code}/executions`            提交Workflow执行

  GET                     `/api/v1/workflow-executions/{execution_id}`              查询执行状态

  GET                     `/api/v1/workflow-executions/{execution_id}/result`       获取正式结果

  POST                    `/api/v1/workflow-executions/{execution_id}/cancel`       申请取消执行

  POST                    `/api/v1/workflow-executions/{execution_id}/resume`       满足条件时恢复执行

  GET                     `/api/v1/workflow-executions/{execution_id}/checkpoint`   查询Checkpoint摘要
  ---------------------------------------------------------------------------------------------------------

Workflow请求：

``` json
{
  "business_type": "resume",
  "business_id": "uuid",
  "input": {},
  "resume_context": null
}
```

执行约束：

-   Workflow定义由代码和配置文件管理；
-   每次执行记录Workflow标识和版本；
-   执行ID、业务ID、任务ID和request_id分别维护；
-   Checkpoint保存中间执行状态，不替代正式业务结果；
-   恢复必须验证原执行状态、当前权限、Checkpoint有效性和恢复条件；
-   不允许将任意历史状态直接恢复为可执行状态；
-   Workflow节点明细写结构化日志，不建立`workflow_node_execution`数据库表；
-   MySQL保存Workflow整体执行摘要和状态；
-   Checkpoint具体后端和MySQL兼容性仍需专项验证。

------------------------------------------------------------------------

## 10. 数字员工与任务调度接口

### 10.1 数字员工

  ------------------------------------------------------------------------------------------------------
  方法                    路径                                                   用途
  ----------------------- ------------------------------------------------------ -----------------------
  GET/POST                `/api/v1/digital-employees`                            数字员工列表/创建

  GET/PATCH               `/api/v1/digital-employees/{employee_id}`              详情/修改

  POST                    `/api/v1/digital-employees/{employee_id}/activate`     启用

  POST                    `/api/v1/digital-employees/{employee_id}/deactivate`   停用

  GET                     `/api/v1/digital-employees/{employee_id}/agents`       查询关联Agent

  PUT                     `/api/v1/digital-employees/{employee_id}/agents`       设置Agent关联

  GET                     `/api/v1/digital-employees/{employee_id}/workflows`    查询关联Workflow

  PUT                     `/api/v1/digital-employees/{employee_id}/workflows`    设置Workflow关联
  ------------------------------------------------------------------------------------------------------

数字员工是业务对象；Agent负责专业AI能力，Workflow负责多步骤流程编排，数字员工负责承接业务任务和调度。三者不能合并为一个对象。

### 10.2 统一任务中心

  方法   路径                                    用途
  ------ --------------------------------------- ------------------
  GET    `/api/v1/tasks`                         任务列表
  POST   `/api/v1/tasks`                         创建通用任务
  GET    `/api/v1/tasks/{task_id}`               任务详情和状态
  POST   `/api/v1/tasks/{task_id}/assignments`   分配任务
  GET    `/api/v1/tasks/{task_id}/assignments`   查询分配信息
  POST   `/api/v1/tasks/{task_id}/cancel`        取消任务
  POST   `/api/v1/tasks/{task_id}/retry`         重试任务
  GET    `/api/v1/tasks/{task_id}/result`        查询正式任务结果
  GET    `/api/v1/tasks/{task_id}/executions`    查询执行摘要

创建请求：

``` json
{
  "task_type": "resume_parse",
  "business_type": "resume",
  "business_id": "uuid",
  "digital_employee_id": "uuid",
  "priority": "normal",
  "parameters": {}
}
```

任务状态统一使用：

  状态          含义
  ------------- ----------
  `pending`     待处理
  `queued`      排队中
  `running`     执行中
  `succeeded`   执行成功
  `failed`      执行失败
  `cancelled`   已取消

状态流转规则：

-   `pending`可进入`queued`或`cancelled`；
-   `queued`可进入`running`或`cancelled`；
-   `running`可进入`succeeded`、`failed`或满足条件的`cancelled`；
-   `failed`只有在允许重试且次数未超限时才可重新排队；
-   `succeeded`为终态，不允许普通重试覆盖原结果；
-   终态变更必须由后端业务规则控制。

任务表保存业务任务状态；`task_execution`保存执行实例摘要、执行序号、重试次数和必要时间；详细执行过程写日志文件。`task_result`只保存正式业务结果或文件引用，不保存普通中间日志。

### 10.3 调度计划

  ---------------------------------------------------------------------------------------------------
  方法                    路径                                                用途
  ----------------------- --------------------------------------------------- -----------------------
  GET/POST                `/api/v1/task-schedules`                            调度计划列表/创建

  GET/PATCH/DELETE        `/api/v1/task-schedules/{schedule_id}`              详情/修改/删除

  POST                    `/api/v1/task-schedules/{schedule_id}/enable`       启用

  POST                    `/api/v1/task-schedules/{schedule_id}/pause`        暂停

  POST                    `/api/v1/task-schedules/{schedule_id}/resume`       恢复

  GET                     `/api/v1/task-schedules/{schedule_id}/executions`   查询执行摘要
  ---------------------------------------------------------------------------------------------------

创建请求：

``` json
{
  "task_id": "uuid",
  "schedule_type": "cron",
  "schedule_expression": "0 9 * * 1-5",
  "timezone": "Asia/Shanghai"
}
```

调度规则：

-   APScheduler负责触发；
-   MySQL保存任务和调度业务状态；
-   独立Worker负责执行；
-   必须保存时区；
-   后端校验Cron表达式和下次执行时间；
-   暂停或删除调度计划不应误删已经产生的业务任务；
-   通过幂等机制避免同一调度时刻重复生成任务。

------------------------------------------------------------------------

## 11. 数据智能与运营决策接口

### 11.1 指标定义

  方法        路径                                     用途
  ----------- ---------------------------------------- ---------------
  GET/POST    `/api/v1/metrics`                        指标列表/创建
  GET/PATCH   `/api/v1/metrics/{metric_id}`            指标详情/修改
  POST        `/api/v1/metrics/{metric_id}/validate`   校验指标配置

动态指标定义存MySQL；固定计算逻辑可由Python代码管理。指标计算口径由后端负责，前端不得自行计算权威业务统计值。

### 11.2 数据分析任务

  方法   路径                                        用途
  ------ ------------------------------------------- --------------
  POST   `/api/v1/analysis-tasks`                    提交分析任务
  GET    `/api/v1/analysis-tasks`                    分析任务列表
  GET    `/api/v1/analysis-tasks/{task_id}`          查询任务状态
  GET    `/api/v1/analysis-tasks/{task_id}/result`   获取分析结果

请求：

``` json
{
  "analysis_type": "recruitment_efficiency",
  "time_range": {
    "start": "2026-10-01T00:00:00Z",
    "end": "2026-11-01T00:00:00Z"
  },
  "dimensions": ["organization_id", "position_id"],
  "filters": {}
}
```

耗时分析异步执行。MySQL保存`analytics_job`状态、参数摘要、结果引用；详细计算过程写Analytics结构化日志。

### 11.3 仪表盘和报告

  方法   路径                                     用途
  ------ ---------------------------------------- ------------------
  GET    `/api/v1/dashboard/overview`             运营总览
  GET    `/api/v1/dashboard/recruitment`          招聘数据看板
  GET    `/api/v1/dashboard/talent`               人才数据看板
  GET    `/api/v1/dashboard/assessment`           测评面试数据看板
  GET    `/api/v1/reports`                        报告列表
  POST   `/api/v1/reports`                        创建报告任务
  GET    `/api/v1/reports/{report_id}`            报告详情
  GET    `/api/v1/reports/{report_id}/download`   报告文件下载

报告文件存文件系统，MySQL保存元数据和文件引用。报表查询必须执行组织数据范围过滤。

------------------------------------------------------------------------

## 12. 通知、导入导出和公共业务接口

本批确认：提供独立业务接口；执行过程使用异步任务和结构化日志，不建立通知、导入或导出专用数据库记录表。需要复用任务中心时，使用通用任务记录，不新增专用记录表。

### 12.1 通知发送

  方法   路径                           用途
  ------ ------------------------------ ------------------
  POST   `/api/v1/notifications/send`   提交通知发送
  POST   `/api/v1/notifications/test`   测试通知渠道配置

请求：

``` json
{
  "channel": "email",
  "recipient": "user@example.com",
  "template_code": "candidate_invitation",
  "variables": {
    "display_name": "用户",
    "invitation_url": "https://example.invalid/invite/..."
  }
}
```

通知发送结果通过通用任务状态和结构化日志追踪。不得因此默认建立通知历史表。通知模板、渠道能力和实际发送配置按既有配置管理原则维护。邀请链接和凭据不得进入普通日志。

### 12.2 数据导入

  方法   路径                                 用途
  ------ ------------------------------------ ------------------
  POST   `/api/v1/imports`                    提交导入任务
  GET    `/api/v1/imports/{task_id}/result`   查询导入结果摘要

请求：

``` json
{
  "file_id": "uuid",
  "target_type": "candidates",
  "options": {
    "validate_only": false
  }
}
```

导入异步执行。文件保存到文件系统；任务过程和行级错误明细写结构化日志或结果文件。导入成功的数据按业务表事务规则写入MySQL。

### 12.3 数据导出

  方法   路径                                 用途
  ------ ------------------------------------ ------------------
  POST   `/api/v1/exports`                    提交导出任务
  GET    `/api/v1/exports/{task_id}/result`   获取导出文件信息

请求：

``` json
{
  "target_type": "candidates",
  "format": "xlsx",
  "filters": {
    "status": ["active"]
  },
  "columns": ["name", "email", "status"]
}
```

导出必须校验字段级和数据范围权限，防止批量泄露个人信息。导出文件通过统一文件下载接口访问；导出过程写结构化日志，不建立专用导出记录表。

------------------------------------------------------------------------

## 13. API健康检查、服务状态和监控接口

### 13.1 接口清单

  方法   路径                                  用途           权限
  ------ ------------------------------------- -------------- ---------------
  GET    `/health`                             基础存活检查   内部/健康探针
  GET    `/api/v1/health`                      API健康状态    按部署策略
  GET    `/api/v1/admin/system/status`         服务状态汇总   管理员
  GET    `/api/v1/admin/system/metrics`        运行指标       管理员
  GET    `/api/v1/admin/system/dependencies`   依赖组件状态   管理员

### 13.2 返回内容

健康检查仅返回服务是否可响应及必要的健康状态，不返回密钥、连接串、内部文件路径和完整异常堆栈。

管理员监控可返回：

-   API请求数量和响应状态分布；
-   请求耗时统计；
-   CPU、内存和GPU资源使用情况（实际采集能力可用时）；
-   MySQL、Milvus、Ollama、MinerU等依赖服务的可用状态；
-   Worker和调度器运行状态；
-   异步任务队列积压或执行统计。

敏感监控接口必须经过管理员权限校验。详细执行过程和异常仍通过日志系统追踪，不将所有日志内容直接暴露为API。

------------------------------------------------------------------------

## 14. 异步任务统一接口约定

### 14.1 异步提交响应

所有耗时业务采用异步模式，成功受理后返回HTTP 202：

``` json
{
  "code": "0",
  "message": "task accepted",
  "data": {
    "task_id": "uuid",
    "status": "pending",
    "status_url": "/api/v1/tasks/uuid"
  },
  "request_id": "req_xxxxx"
}
```

Agent/Workflow专用执行接口可以同时返回`execution_id`。`task_id`、`execution_id`、业务对象ID和`request_id`各自具有独立语义，不能混用。

### 14.2 状态查询

``` http
GET /api/v1/tasks/{task_id}
```

响应`data`：

``` json
{
  "task_id": "uuid",
  "task_type": "resume_parse",
  "status": "running",
  "progress": {
    "current": 2,
    "total": 4,
    "stage": "extracting"
  },
  "created_at": "2026-11-03T10:00:00Z",
  "started_at": "2026-11-03T10:00:05Z",
  "completed_at": null,
  "error": null
}
```

`progress`为可选信息。业务无法准确计算百分比时，返回阶段和状态，不伪造精确进度。

### 14.3 结果查询

``` http
GET /api/v1/tasks/{task_id}/result
```

-   任务未完成：返回业务错误`INVALID_STATE_TRANSITION`或明确的未就绪状态；
-   成功：返回正式结果摘要或结果资源引用；
-   失败：返回安全的错误摘要和可否重试信息；
-   取消：返回取消状态，不返回伪造成功结果。

### 14.4 取消与重试

``` http
POST /api/v1/tasks/{task_id}/cancel
POST /api/v1/tasks/{task_id}/retry
```

取消是受控动作，不保证任意运行中的底层操作都能瞬间停止。后端必须确认任务类型支持取消、操作者有权限，并记录最终状态。

重试前检查：任务是否失败、是否可重试、重试次数是否超限、业务数据是否仍有效、原任务是否仍在执行。重试创建新的执行实例或执行序号，不覆盖原执行日志。

### 14.5 HTTP轮询

初期采用HTTP轮询，不引入强制SSE或WebSocket。前端根据任务类型和服务端状态采用适当轮询间隔；任务进入终态后停止轮询。前端关闭页面不代表后台任务自动取消。

------------------------------------------------------------------------

## 15. 权限与数据范围矩阵

  ---------------------------------------------------------------------------------------
  资源/操作            普通业务用户     招聘/测评业务人员   组织管理员     系统管理员
  -------------------- ---------------- ------------------- -------------- --------------
  查看本人可访问人才   按授权           按授权              管理范围内     按系统授权

  创建/修改候选人      按业务授权       按业务授权          管理范围内     按系统授权

  简历上传/下载        仅授权业务对象   仅授权业务对象      管理范围内     按系统授权

  人才画像生成         不默认开放       按授权              管理范围内     按系统授权

  画像审核/发布        不默认开放       指定审核权限        管理范围内     按系统授权

  测评方案管理         不默认开放       按授权              管理范围内     按系统授权

  答题和面试评价       按任务授权       按分配角色          管理范围内     按系统授权

  Agent/Workflow执行   仅开放能力       按业务授权          管理范围内     管理权限

  数字员工和调度       不默认开放       按授权              管理范围内     管理权限

  指标与分析           受限查询         业务范围内          组织范围内     管理权限

  用户、角色和权限     本人有限操作     不默认开放          授权范围内     管理权限

  系统监控             不允许           不允许              按授权         允许
  ---------------------------------------------------------------------------------------

本表是API层面的权限基线。实际角色编码、权限点和数据范围枚举必须与《权限设计说明》和《系统安全、权限与审计详细设计》保持一致。前端菜单隐藏不能替代后端授权。

------------------------------------------------------------------------

## 16. 数据库关联与事务边界

  ------------------------------------------------------------------------------------------------------------------------------------------------
  API业务                 主要数据库对象                                   事务边界
  ----------------------- ------------------------------------------------ -----------------------------------------------------------------------
  项目、岗位和招聘需求    项目群、项目、项目需求、岗位、招聘需求           单次资源写入及必要关联在同一事务

  候选人                  统一人才主体/候选人视图                          主体创建与必要业务关联事务化

  简历上传                `common_file`、`candidate_resume`                文件落盘与数据库元数据采用补偿清理；不假定文件系统和MySQL天然原子事务

  简历解析                `candidate_resume`、通用任务、执行摘要           先提交任务，再由Worker执行；最新解析结果成功后更新

  匹配与筛选              匹配结果、选拔记录、通用任务                     任务状态和正式结果分阶段提交

  人才经历、技能、标签    经历、技能字典、关联表、标签字典、关联表         单次集合更新在事务内完成

  人才画像                画像、版本、审核记录                             版本创建、审核和发布按状态事务化

  测评                    方案、题目、关联表、任务、答题评分、报告         任务创建时保存方案快照；答题提交需防重复

  面试                    面试、评价                                       面试安排和面试官关联事务化

  Agent/Workflow          执行摘要、Checkpoint外部持久化                   执行状态和Checkpoint不是天然同一事务，需失败补偿和一致性检查

  数字员工与任务          数字员工、关联表、任务、分配、调度、执行、结果   任务创建和分配需保证状态一致；Worker执行单独事务

  数据智能                指标定义、分析任务、结果、报告                   分析任务先持久化，完成后保存正式结果

  用户与权限              用户、组织、角色、权限及关联表                   角色授权集合更新在事务内完成

  文件                    `common_file`                                    文件操作与元数据使用补偿策略

  通知/导入导出           通用任务、文件和结构化日志                       不新增专用记录表；业务导入结果按业务表事务提交
  ------------------------------------------------------------------------------------------------------------------------------------------------

### 16.1 与运行日志的边界

数据库详细设计已确认：

-   `agent_execution`：MySQL保留执行摘要和状态；
-   `workflow_execution`：MySQL保留整体执行状态；
-   `task_execution`：MySQL保留执行实例、状态和重试；
-   `analytics_job`：MySQL保留分析任务状态；
-   `workflow_node_execution`：不建立MySQL表，节点明细进入结构化日志；
-   Agent模型调用、Tool调用、Worker内部步骤和分析过程进入日志；
-   `task_result`只保存正式业务结果，不保存普通中间过程。

API响应中的执行摘要不得依赖扫描全部日志文件即时拼装。日志查询能力按独立运维工具或后续受控管理接口规划。

------------------------------------------------------------------------

## 17. Pydantic Schema与OpenAPI管理

### 17.1 Schema组织建议

``` text
app/
└── schemas/
    ├── common.py
    ├── auth.py
    ├── user.py
    ├── organization.py
    ├── file.py
    ├── project.py
    ├── position.py
    ├── recruitment.py
    ├── candidate.py
    ├── resume.py
    ├── talent.py
    ├── talent_profile.py
    ├── assessment.py
    ├── interview.py
    ├── agent.py
    ├── workflow.py
    ├── task.py
    ├── digital_employee.py
    ├── analytics.py
    └── monitoring.py
```

公共Schema建议：

-   `ApiResponse[T]`：统一成功响应；
-   `ApiErrorResponse`：统一错误响应；
-   `PaginationParams`：分页参数；
-   `PageData[T]`：列表分页数据；
-   `SortParams`：排序参数；
-   `FieldValidationError`：字段级错误；
-   `TaskStatusResponse`：异步任务状态。

### 17.2 Schema复用落地方式

-   通过公共字段基类、嵌套Schema和泛型分页Schema复用；
-   创建、修改、列表、详情响应根据业务约束拆分；
-   使用Pydantic字段校验器和枚举约束；
-   统一配置日期时间序列化；
-   对敏感字段使用独立响应模型，不通过简单排除字段来依赖前端安全。

### 17.3 OpenAPI与TypeScript同步

``` text
Pydantic Schema
      |
      v
FastAPI OpenAPI
      |
      v
前端TypeScript类型生成/同步
      |
      v
类型差异检查
      |
      v
接口测试与前后端联调
```

FastAPI自动生成OpenAPI文档。具体TypeScript类型生成工具和自动化命令在工程实现阶段选定并纳入版本管理。接口契约变化必须检查前后端兼容性。

------------------------------------------------------------------------

## 18. 安全、审计与请求追踪

### 18.1 API安全要求

-   所有受保护接口验证JWT和用户状态；
-   所有资源查询和写入执行权限检查；
-   组织数据范围在后端查询层和业务层执行；
-   文件下载、预览和删除重新验证业务对象权限；
-   登录、文件上传、AI任务提交等高风险接口实施限流；
-   对关键写操作使用幂等机制；
-   不在响应中暴露密码哈希、Token、密钥和内部堆栈；
-   CORS、HTTPS、CSRF相关措施按Bearer Token实际存储方式和部署方式配置；
-   AI Tool必须在服务端注册和授权，不允许客户端任意指定后端函数或SQL。

### 18.2 request_id追踪

每个HTTP请求生成或校验`request_id`，在响应头和统一响应体中返回。异步任务提交时，将原始请求ID与任务ID、执行ID和业务对象ID关联。

建议追踪字段：

-   `request_id`
-   `task_id`
-   `execution_id`
-   `business_type`
-   `business_id`
-   `actor_id`
-   `correlation_id`

这些标识用途不同，不能相互替代。

### 18.3 审计与日志

关键操作包括用户/角色授权变更、组织调整、关键人才数据修改、文件访问和删除、Agent/Workflow执行控制、测评结果审核和报告发布。

根据数据库设计，操作审计和系统运行日志使用文件管理，逻辑分离。日志不得记录密码、JWT、Refresh
Token、邀请凭据、API Key或不必要的完整个人信息。

------------------------------------------------------------------------

## 19. 接口目录总览

以下按业务资源归类，供前后端开发拆分任务和生成OpenAPI标签使用。

  ------------------------------------------------------------------------------------------------------------------------------------------------------------
  模块                                资源前缀
  ----------------------------------- ------------------------------------------------------------------------------------------------------------------------
  认证                                `/api/v1/auth`

  用户                                `/api/v1/users`

  组织                                `/api/v1/organizations`

  角色与权限                          `/api/v1/roles`、`/api/v1/permissions`

  文件                                `/api/v1/files`、`/api/v1/file-links`

  项目与项目群                        `/api/v1/project-groups`、`/api/v1/projects`、`/api/v1/project-requirements`

  岗位与招聘                          `/api/v1/positions`、`/api/v1/recruitments`

  候选人与简历                        `/api/v1/candidates`、`/api/v1/resumes`、`/api/v1/resume-parses`

  筛选与匹配                          `/api/v1/screening-tasks`、`/api/v1/matches`、`/api/v1/match-results`

  人才档案                            `/api/v1/talents`、`/api/v1/talent-experiences`、`/api/v1/skills`、`/api/v1/tags`

  人才画像                            `/api/v1/talent-profiles`、`/api/v1/talent-profile-versions`

  测评                                `/api/v1/assessment-plans`、`/api/v1/assessment-questions`、`/api/v1/assessment-tasks`、`/api/v1/assessment-responses`

  面试                                `/api/v1/interviews`、`/api/v1/interview-evaluations`

  Agent                               `/api/v1/agents`、`/api/v1/agent-executions`

  Workflow                            `/api/v1/workflows`、`/api/v1/workflow-executions`

  数字员工                            `/api/v1/digital-employees`

  任务                                `/api/v1/tasks`、`/api/v1/task-schedules`

  数据智能                            `/api/v1/metrics`、`/api/v1/analysis-tasks`、`/api/v1/dashboard`、`/api/v1/reports`

  公共业务                            `/api/v1/notifications`、`/api/v1/imports`、`/api/v1/exports`

  系统监控                            `/api/v1/health`、`/api/v1/admin/system`
  ------------------------------------------------------------------------------------------------------------------------------------------------------------

------------------------------------------------------------------------

## 20. 测试与验收标准

### 20.1 API测试范围

  测试类型       测试内容
  -------------- ------------------------------------------------
  路由与方法     路径、HTTP方法和资源语义
  请求Schema     必填、类型、长度、范围、枚举和格式
  响应Schema     成功、错误、分页和字段可见性
  认证           无Token、无效Token、过期Token、退出和刷新
  邀请           未过期、过期、重复使用、撤销和账号状态
  权限           角色权限、资源级权限和操作权限
  数据范围       跨组织访问、越权查询、越权修改
  文件           文件类型、大小、上传、关联、下载、预览、删除
  人才业务       项目、岗位、招聘、候选人、简历、匹配和画像
  测评面试       方案快照、答题重复提交、评分复核、报告访问
  AI执行         Agent/Workflow启动、状态、结果、取消和恢复条件
  任务调度       创建、分配、暂停、恢复、取消、重试和幂等
  数据智能       指标权限、异步分析和报告下载
  监控           普通用户不可访问敏感监控接口
  前后端联调     OpenAPI、TypeScript类型和真实响应一致
  异常与可靠性   超时、依赖服务失败、日志关联和重复提交

### 20.2 关键验收场景

-   [ ] 用户只能通过管理员邀请流程获得账号，不开放公开注册。
-   [ ] 用户名和邮箱均可使用同一个登录接口。
-   [ ] 所有受保护接口验证JWT Bearer Token。
-   [ ] 后端自动应用角色、组织和数据范围限制。
-   [ ] 文件上传先创建资源，再通过文件ID关联业务对象。
-   [ ] 无权访问的文件不能通过猜测文件ID下载。
-   [ ]
    简历解析、筛选、匹配、测评分析、Agent、Workflow和数据分析均可异步执行。
-   [ ] 异步接口返回任务ID或执行ID，HTTP轮询能够获取状态。
-   [ ] 任务取消和重试遵循状态机和权限约束。
-   [ ] 候选人和人才档案映射到统一人才主体，不产生重复自然人主档案。
-   [ ] 人才画像保留版本，正式发布经过审核。
-   [ ] 测评任务保存执行时方案快照。
-   [ ] AI评分和面试分析不未经复核直接成为最终业务决定。
-   [ ] Agent/Workflow定义不通过MySQL配置表动态管理。
-   [ ] Workflow节点明细写日志，不建立`workflow_node_execution`表。
-   [ ] 通知、导入导出过程不建立专用记录表。
-   [ ] 系统监控敏感信息只向管理员开放。
-   [ ] 所有响应和错误包含可追踪的`request_id`。
-   [ ] OpenAPI与Pydantic Schema保持一致，前端TypeScript类型可同步。
-   [ ] 权限、文件、任务、异常和跨模块联调测试通过。

------------------------------------------------------------------------

## 21. 待实施时明确的参数与验证事项

以下内容没有在30项确认中确定具体数值或最终技术细节，实施前需要通过安全评审、接口性能测试或专项验证明确，不应在设计阶段虚构：

1.  JWT Access Token和Refresh Token有效期、轮换和多设备会话策略；
2.  浏览器端Token存储策略及相应XSS防护；
3.  邀请链接有效期的最终数值、重发和撤销策略；
4.  登录、上传、AI执行和导出接口的限流阈值；
5.  文件大小、文件类型和预览白名单；
6.  各异步任务的超时、重试次数、取消语义和结果保留期限；
7.  具体角色编码、权限点、数据范围枚举和显式拒绝优先级；
8.  Checkpoint后端和当前LangGraph版本的兼容性；
9.  OpenAPI到TypeScript的具体类型生成工具及CI命令；
10. 监控指标采集范围及资源采集组件的实际可用性。

------------------------------------------------------------------------

## 22. 本步骤最终结论

### 22.1 确认情况

-   第一批：6项完成；
-   第二批：6项完成；
-   第三批：6项完成；
-   第四批：6项完成；
-   第五批：6项完成；
-   总计：30项全部确认完成。

### 22.2 最终设计结论

本平台API采用RESTful风格、统一`/api/v1/`前缀、统一响应结构、页码分页、Pydantic数据校验和OpenAPI契约管理。

认证采用JWT Bearer
Token；账号采用管理员邀请制；数据范围由后端自动计算；文件采用"先上传、后关联"的两步模式，下载和预览由后端鉴权后返回文件流。

七大业务模块按独立资源设计。耗时AI业务采用异步任务和HTTP轮询。Agent与Workflow分别提供执行接口，数字员工与任务调度保持独立。通知、导入导出使用业务接口、通用任务能力和结构化日志，不增加专用记录表。

### 22.3 下一步

第五阶段第04步API接口详细设计完成。下一步建议进入**第五阶段第05步：前端页面与交互详细设计**，将本文件中的接口资源、字段、状态和权限映射为页面、组件、操作流程及前端路由。

本文件是接口设计基线，不代表所有API已经编码、部署或通过测试。实际开发以Pydantic
Schema、OpenAPI和数据库字段评审结果为准。
