export const modules = [
  { title: '概览', items: [['dashboard', '智能工作台']] },
  {
    title: '人才选拔',
    items: [
      ['resume', '简历智能筛选'],
      ['match', '岗位-人才匹配'],
    ],
  },
  { title: '人才档案与人才画像', items: [['talent', '人才画像档案']] },
  { title: '智能测评与面试', items: [['exam', '智能测评与面试']] },
  { title: 'AI Agent 与工作流管理', items: [['agent', 'Agent 编排中心']] },
  { title: '数字员工与任务调度', items: [['employee', '数字员工与任务调度']] },
  { title: '数据智能与运营决策', items: [['data', '智能问数与决策']] },
  {
    title: '用户、组织与权限管理',
    items: [
      ['system', '系统管理'],
      ['stack', '系统技术状态与服务监控'],
    ],
  },
]
// 菜单过滤仅控制展示，不能替代后端授权。
export function filterMenus(allowed?: string[]) {
  return modules
    .map((g) => ({ ...g, items: g.items.filter(([id]) => !allowed || allowed.includes(id!)) }))
    .filter((g) => g.items.length)
}
export const pageLoaders = {
  dashboard: () => import('@/views/dashboard/DashboardView.vue'),
  resume: () => import('@/views/talent-selection/ResumeView.vue'),
  match: () => import('@/views/talent-selection/MatchView.vue'),
  talent: () => import('@/views/talent-profile/TalentView.vue'),
  exam: () => import('@/views/assessment/ExamView.vue'),
  agent: () => import('@/views/agent-workflow/AgentView.vue'),
  employee: () => import('@/views/digital-employee/EmployeeView.vue'),
  data: () => import('@/views/analytics/DataView.vue'),
  system: () => import('@/views/system/SystemView.vue'),
  stack: () => import('@/views/system/StackView.vue'),
}
