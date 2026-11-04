export const agents = [
  { id: 'profile-parser', name: '档案解析 Agent', description: '多格式解析 · 标签抽取 · 查重合并' },
  {
    id: 'assessment-analyst',
    name: '测评分析 Agent',
    description: '自适应出题 · 能力研判 · 错题复盘',
  },
  { id: 'job-matcher', name: '岗位匹配 Agent', description: '匹配打分 · 原因解释' },
  { id: 'data-advisor', name: '数据决策 Agent', description: '数据分析 · 决策报告' },
] as const
export type AgentId = (typeof agents)[number]['id']
export function agentName(id: AgentId) {
  return agents.find((a) => a.id === id)!.name
}
export const employees: { id: string; name: string; role: string; agentIds: AgentId[] }[] = [
  { id: 'resume-assistant', name: '简历助手', role: '档案整理', agentIds: ['profile-parser'] },
  {
    id: 'hiring-assistant',
    name: '招聘助手',
    role: '招聘协作',
    agentIds: ['job-matcher', 'assessment-analyst'],
  },
  { id: 'data-assistant', name: '数据助手', role: '运营分析', agentIds: ['data-advisor'] },
]
