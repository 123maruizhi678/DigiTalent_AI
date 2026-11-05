# M1-GATE-R09 测试与验收报告

## 测试范围与环境

2026-11-04，Windows/PowerShell；后端使用现有D:/anaconda3/envs/feiyu/python.exe，前端使用现有Node/npm/node_modules。没有升级依赖、读取真实.env、启动服务或连接数据库。本次验证契约组件和前端HTTP适配器行为，以及既有全量回归；不冒充真实IAM业务验证。

## 命令与结果

项目根目录：

- `D:/anaconda3/envs/feiyu/python.exe -m ruff check app tests`：通过。
- `D:/anaconda3/envs/feiyu/python.exe -m ruff format --check app tests`：通过，21文件。
- `D:/anaconda3/envs/feiyu/python.exe -m pytest -q`：最终69通过、0失败（新增16个契约用例，含参数化）。

frontend目录：

- `npm run test:run`：最终5文件、27用例通过、0失败（新增4个认证用例）。
- `npm run type-check`：通过。
- `npm run lint`：全量通过；最终修改后另以 `npx eslint src/api/request.ts src/api/auth.ts tests/auth.test.ts` 检查变更文件。
- `npx prettier --check src/api/request.ts src/api/auth.ts tests/auth.test.ts`：变更文件格式通过。
- `npm run build`：通过，2310模块；既有chunk大于500kB警告，不影响构建；Vitest提示未来native配置加载兼容性警告，本次未改无关配置。

首次使用默认D:/anaconda3/python.exe执行ruff/pytest失败：缺ruff、pydantic_settings.exceptions。切换README指定的现有feiyu环境后成功；没有安装包，初始失败不隐瞒，不计为业务测试失败。

## 已执行测试用例与安全检查

后端：开发/生产Cookie设置及清理属性（HttpOnly、Secure、Lax、Path、host-only、Max-Age、no-store），精确Origin/伪造域/null/缺失/缺头拒绝，响应不允许Refresh或密码字段，密码repr隐藏，Cookie剩余期限及越界拒绝。
前端：同时间只调用一次刷新、withCredentials/CSRF头/版本前缀；退出时迟到刷新不恢复内存身份；新登录失败不保留旧令牌；资源401刷新后最多重试一次。测试使用合成令牌和适配器，无真实凭据。
既有pytest及Vitest用例全量回归通过；既有日志/异常基础设施测试也包含在69项内。日志不采集请求头/正文，但没有真实认证事件可供泄露验证，不能将其标为通过。

## 未执行项目、原因及失败项目

后端独立类型检查：项目未配置mypy/pyright，不擅自添加依赖；前端vue-tsc已执行。
真实登录正确/错误/停用、密码哈希、JWT签名与过期、真实Refresh过期/轮换/并发/重放、数据库事务与撤销、退出幂等及退出后旧Token拒绝、当前用户停用与权限、认证日志完整Token/密码/Cookie泄露、浏览器CSRF与Cookie落地、跨标签页互斥及生产HTTPS：均未执行，原因是当前没有IAM接口、用户模型、持久化会话和实际生产部署。未以skip占位测试冒充完成。
最终已执行测试0失败；缺失能力属于未实现/未验证，不计为通过。

## 文件变更清单

新增：app/common/auth_contract.py（响应白名单、Cookie及CSRF组件）；tests/unit/test_auth_contract.py；frontend/tests/auth.test.ts；本目录三个R09交付文件。
修改：frontend/src/api/request.ts（统一版本、内存Bearer、刷新合并与竞态处理）；frontend/src/api/auth.ts（真实契约路径与Envelope）；指定API设计第7.1节及安全设计第3.1节/第18节第3项。
AGENTS.md经检查已存在用户要求的完整配置章节，未重复添加、未改其他规则。无数据库迁移、环境配置变更或新增依赖。保留初始工作区变更，没有Git Commit。

## 遗留问题与最终验收状态

部分完成，R09门禁未关闭。须由P6-IAM-004/005完成真实账号、JWT和持久化会话，再执行上述未执行业务矩阵；前端FE-002/003/004接入实际状态、跨标签页互斥与错误交互。生产Origin/HTTPS/反向代理及Cookie行为需人工部署验收。设计确认不等于运行时已实现。

## 本轮审核整改与测试范围

上述为原轮次记录，完整保留。本轮只修改指定三份文档，未重跑历史69项后端或27项前端测试，不将历史结果作为本轮结果。新增测试仅验证文档契约条款、JSON示例及一致性，不证明真实认证业务通过。测试源码嵌入本报告，避免新增第四个文件。

环境核对：Conda feiyu，Python 3.11.18；解释器D:/anaconda3/envs/feiyu/python.exe；pip 26.2.2，模块路径D:/anaconda3/envs/feiyu/Lib/site-packages/pip，入口D:/anaconda3/envs/feiyu/Scripts/pip.exe；pytest入口同环境Scripts/pytest.exe。执行conda env list、PowerShell Conda hook初始化、conda activate feiyu、python --version、sys.executable、python -m pip --version及Get-Command。初次未初始化hook时激活未生效，只核查环境，随后正确激活；未使用系统Python执行本轮脚本。

### 可复现文档契约测试

在根目录已激活feiyu后执行下面代码块；可将代码块提取后通过python标准输入运行，不创建文件。只读取两份指定契约文档，无目录扫描。

```python
import json
import re
import unittest
from pathlib import Path

root = Path('D:/AI/DigiTalent_AI/docs/开发日记/1104')
names = ['M1-GATE-R09_API接口契约.md', 'M1-GATE-R09_RefreshToken与HttpOnlyCookie认证契约决策.md']
texts = [(root / n).read_text(encoding='utf-8') for n in names]

class DocumentContractTests(unittest.TestCase):
    def require(self, *terms):
        for text in texts:
            for term in terms:
                self.assertIn(term, text)

    def test_error_codes(self):
        self.require('| CSRF校验失败 | 403 | CSRF_ERROR |', '| 业务权限不足 | 403 | PERMISSION_ERROR |', '| Token或会话失效 | 401 | AUTHENTICATION_ERROR |')
        for text in texts:
            self.assertNotIn('403 PERMISSION_ERROR：CSRF', text)

    def test_json_examples(self):
        for text in texts:
            examples = [json.loads(s) for s in re.findall(r'```json\n(.*?)\n```', text, re.S)]
            self.assertTrue({'CSRF_ERROR', 'PERMISSION_ERROR', 'AUTHENTICATION_ERROR'} <= {e['code'] for e in examples})
            for e in examples:
                self.assertEqual(set(e), {'code', 'message', 'data', 'request_id'})

    def test_csrf_no_mutation(self):
        self.require('CSRF失败不得修改会话状态', '不得清理用户Cookie', '不返回Set-Cookie', '403不触发自动刷新')

    def test_all_protected_apis(self):
        self.require('P6-IAM-005', '所有受保护API', '统一认证依赖', '会话必须存在、未撤销、未过期且关联用户启用', 'sub必须与会话user_id一致', '不能仅在/auth/me检查会话')

    def test_jwt_and_keys(self):
        self.require('固定HS256', 'iss', 'aud', 'sub', 'sid', 'iat', 'exp', 'jti', '0 < exp-iat <= 900', '时钟宽限为0秒', 'UUIDv4', '至少32随机字节', '均无默认值', 'SecretStr', '未知kid拒绝', '密钥泄露时立即移除')

    def test_refresh_and_session(self):
        self.require('secrets.token_bytes(32)', '43个ASCII字符', 'BINARY(32)', '原始Refresh Token不得持久化', '摘要不得作为客户端认证凭据', 'session_id', 'user_id', 'token_family_id', 'refresh_token_hash', 'token_generation', 'created_at', 'expires_at', 'revoked_at', 'last_used_at', 'status', '未到期的已消费摘要不能提前删')

    def test_transaction_order(self):
        for text in texts:
            section = text.split('数据库操作顺序固定：', 1)[1].split('CAS失败', 1)[0]
            self.assertEqual(re.findall(r'^([1-9])\. ', section, re.M), list('123456789'))
        self.require('SELECT FOR UPDATE', '受影响行数必须为1', 'expires_at保持不变', '失败响应不携带新令牌或Set-Cookie', '第二个识别重放后整族撤销')

    def test_network_recovery(self):
        self.require('不采用安全幂等恢复机制', '不自动重试刷新', '需重新登录', '阻止排队和新的资源请求继续触发刷新', '再次使用旧Cookie必须视为重放', '不增加Redis或缓存')

    def test_concurrency(self):
        self.require('单标签页多个业务401共用一个Promise', '原业务请求最多重试一次', 'generation', 'digitalent-auth-session', 'Web Locks', 'BroadcastChannel', '不传播任何Token', '本次未实现', '迟到Set-Cookie')

    def test_consistency(self):
        sections = [t.split('## 审核整改：错误码与前端处理', 1)[1].split('## 本轮整改验收结论', 1)[0].strip() for t in texts]
        self.assertEqual(sections[0], sections[1])
        self.require('Field(description=', '本次只修订三份R09文件')

if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(DocumentContractTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(not result.wasSuccessful())
```

### 未执行的业务与浏览器验收

- 运行时错误码：CSRF失败403 CSRF_ERROR且无会话/Cookie变更；权限不足403 PERMISSION_ERROR；Token失效401 AUTHENTICATION_ERROR。
- 统一认证依赖：有效JWT/会话允许访问；无效JWT、缺失/撤销/过期会话和停用用户拒绝；除/auth/me之外的业务资源使用同一依赖。
- 轮换：有效Token、旧Token重放、并发、CAS及事务失败、响应丢失恢复、绝对到期不延长。
- 安全：密钥和认证信息不入日志；原始Refresh不入数据库或JSON；摘要不能作为客户端凭据。
- 浏览器及生产：Web Locks/BroadcastChannel、完整客户端状态机、迟到Set-Cookie、Origin/HTTPS/Cookie部署、密钥滚动与泄露后的全实例处置。

原因：本轮仅明确技术契约，IAM与完整前端状态机尚未实现。既有组件和请求层仍须在后续接入时落实CSRF_ERROR映射、统一依赖及网络恢复策略；不能因文档测试通过宣称运行时已符合。没有修改其他代码、正式设计文档、依赖或配置，没有迁移或Git Commit。

### 本轮实际命令与结果

根目录执行（使用已核对的feiyu解释器）：

```powershell
@'
from pathlib import Path
p=Path('docs/开发日记/1104/M1-GATE-R09_测试与验收报告.md')
s=p.read_text(encoding='utf-8')
code=s.split('```python\n',1)[1].split('\n```\n',1)[0]
exec(compile(code,str(p)+'::contract-tests','exec'), {'__name__':'__main__'})
'@ | & 'D:\anaconda3\envs\feiyu\python.exe' -
```

最终结果：10项通过，0失败，0跳过。初次测试提取器使用unittest.main配合动态exec未发现用例，输出0项；该结果不计通过。修正为显式加载DocumentContractTests后实际执行10项。另一次构造编辑脚本因PowerShell here-string嵌套解析失败，未产生修改，随后改用补丁完成。未掩盖失败或空测试结果。

回归范围为三文档错误示例JSON解析、既有错误合并条款消除、两份整改规范逐字一致、历史测试记录保留和仅指定三文件写入核对；没有重跑应用回归或未实现业务测试。最终文档检查以追加验收结论后的复跑结果为准。

## 本轮整改验收结论

已完成（R09设计门禁）。四项整改均已纳入技术契约，10项文档契约检查通过。原轮次“部分完成”是历史运行时业务口径，予以保留；本轮按用户明确的设计门禁口径判定，不代表真实IAM已开发或业务验收通过。前述业务、浏览器和生产验证继续作为后续IAM/前端接入条件，不自动开始R10或IAM。
