import { defineStore } from 'pinia'
import { agents } from '@/config/agents'
export interface WorkspaceRecord {
  id: number
  name: string
  detail: string
  status: string
}
const examples: Record<string, string[]> = {
  候选人管理: ['陈 * 宇', '高级算法工程师 · 硕士 · 6 年经验'],
  招聘流程管理: ['算法岗位招聘', '简历筛选 → 测评 → 面试 → 录用'],
  人才标签: ['LLM 微调', '技术栈 / LoRA / vLLM'],
  人才能力分析: ['陈 * 宇能力分析', '技术深度 94 / 工程能力 88 / 协作沟通 78'],
  题库管理: ['单选题示例', '单选、多选、判断、填空、简答五种题型见在线测评'],
  测评任务: ['算法能力测评', '40 题 / 90 分钟 / 高级算法工程师'],
  面试管理: ['陈 * 宇技术面试', '2026-11-05 14:00 / 面试官：张敏'],
  面试评价: ['陈 * 宇面试评价', '技术深度：优秀；工程实践：良好；建议：进入复试'],
  'Agent 配置': [agents[0].name, '输入：简历文本；输出：结构化标签；超时：30s'],
  'Prompt 管理': ['简历标签抽取', '请从候选人简历中提取技能、学历与经验，返回 JSON。'],
  'Tools 管理': ['演示解析工具', '输入 text:string；输出 tags:string[]；仅本地模拟'],
  'Workflow 管理': ['招聘筛选流程', '简历上传 → 档案解析 → 岗位匹配 → 人工复核'],
  工作流执行记录: ['招聘流程 #2486', '模拟完成 / 耗时 412ms / 无真实接口调用'],
  组织管理: ['AI 平台事业部', '下属：算法组、产品组；负责人：刘 * 强'],
  权限管理: ['HR 管理员', '功能：简历、测评；数据范围：本部门；后端未接入'],
}
export const useWorkspaceStore = defineStore('workspace', {
  state: () => ({ entries: {} as Record<string, WorkspaceRecord[]>, nextId: 100 }),
  actions: {
    list(section: string) {
      if (!this.entries[section]) {
        const sample = examples[section] ?? [section + '示例', '本地演示配置，可编辑保存']
        this.entries[section] = [
          { id: this.nextId++, name: sample[0]!, detail: sample[1]!, status: '启用' },
        ]
      }
      return this.entries[section]!
    },
    save(section: string, id: number | null, data: Omit<WorkspaceRecord, 'id'>) {
      const rows = this.list(section)
      const row = rows.find((r) => r.id === id)
      if (row) Object.assign(row, data)
      else rows.push({ ...data, id: this.nextId++ })
    },
    remove(section: string, id: number) {
      this.entries[section] = this.list(section).filter((r) => r.id !== id)
    },
    status(section: string, id: number, status: string) {
      const row = this.list(section).find((r) => r.id === id)
      if (row) row.status = status
    },
  },
})
