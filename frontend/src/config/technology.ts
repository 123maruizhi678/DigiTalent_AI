export const technicalStatuses = {
  已确认: '技术方案已确认，不代表已安装或启动',
  已安装: '有安装记录，不代表已启动',
  已启动: '有启动证据，不代表持续可用',
  待部署: '尚未完成部署',
  待验证: '缺少检查证据',
  暂不采用: '当前阶段不采用',
  未确认: '尚未确定方案',
}
export const technologies = [
  {
    name: 'Vue 3 / TypeScript / Vite / Element Plus',
    category: '前端技术',
    status: '已安装',
    deployment: 'npm 本地工程',
    version: '以 package.json 为准',
  },
  {
    name: 'FastAPI / SQLAlchemy',
    category: '后端技术',
    status: '已确认',
    deployment: '待验证',
    version: '待验证',
  },
  {
    name: 'LangChain / LangGraph',
    category: 'AI 应用框架',
    status: '已确认',
    deployment: '待验证',
    version: '待验证',
  },
  {
    name: 'Ollama',
    category: '大模型服务',
    status: '已确认',
    deployment: '本地服务，部署待验证',
    version: '待验证',
  },
  {
    name: 'MinerU',
    category: '文档解析',
    status: '已确认',
    deployment: 'Conda + pip',
    version: '待验证',
  },
  {
    name: 'MySQL',
    category: '业务数据库',
    status: '已确认',
    deployment: '待验证',
    version: '8.0（确认方案）',
  },
  {
    name: 'Milvus',
    category: '向量数据库',
    status: '待部署',
    deployment: 'Docker Run',
    version: '待验证',
  },
  {
    name: 'Windows 11 / Conda AI / Python 3.11',
    category: '开发与部署工具',
    status: '已确认',
    deployment: '本地环境',
    version: 'Windows 11 / Python 3.11',
  },
  {
    name: 'Redis / Docker Compose',
    category: '开发与部署工具',
    status: '暂不采用',
    deployment: '不部署',
    version: '—',
  },
]
export const services = ['FastAPI', 'MySQL', 'Milvus', 'Ollama', 'MinerU'].map((name) => ({
  name,
  address: '待接入',
  status: '未连接 / 未检测',
  deployment:
    name === 'Milvus' ? 'Docker Run（待部署）' : name === 'MinerU' ? 'Conda + pip' : '待验证',
  version: name === 'MySQL' ? '8.0（确认方案）' : '待验证',
  checkedAt: '尚未检查',
}))
export const technicalTodos = [
  'Milvus 尚未部署；其余服务安装与启动状态待验证。',
  '服务地址、实际版本和监控接口待提供。',
  '性能、并发、可用性和准确率均未实测，不显示达标结论。',
  '未确认的选型保持未确认，不添加组件；后端认证及数据范围校验待接入。',
]
