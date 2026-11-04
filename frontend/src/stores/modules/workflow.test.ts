import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useWorkflowStore } from './workflow'
import { useUserStore } from './user'
import { agents, employees } from '@/config/agents'
beforeEach(() => setActivePinia(createPinia()))
describe('Workflow 配置与模拟边界', () => {
  it('删除节点时清理连线，断连流程无法保存', () => {
    const s = useWorkflowStore()
    s.remove(2)
    expect(s.edges).toHaveLength(0)
    expect(() => s.save()).toThrow('未连接')
  })
  it('拒绝无效、自连、重复连线和环路', () => {
    const s = useWorkflowStore()
    expect(() => s.connect({ source: 1, target: 1, condition: '' })).toThrow()
    expect(() => s.connect({ source: 1, target: 99, condition: '' })).toThrow()
    expect(() => s.connect({ source: 1, target: 2, condition: '' })).toThrow()
    s.connect({ source: 2, target: 1, condition: '' })
    expect(() => s.save()).toThrow('无环')
  })
  it('保存快照独立于后续编辑，并按连接顺序模拟', async () => {
    vi.useFakeTimers()
    try {
      const s = useWorkflowStore()
      s.save()
      s.description = '新描述'
      expect(JSON.parse(s.saved).description).not.toBe(s.description)
      s.nodes.reverse()
      const run = s.simulate()
      expect(s.running).toBe(true)
      await vi.runAllTimersAsync()
      await run
      expect(s.running).toBe(false)
      expect(s.logs[1]).toContain('简历上传')
      expect(s.logs.at(-1)).toContain('未生成真实业务结果')
    } finally {
      vi.useRealTimers()
    }
  })
  it('拒绝空名称、缺少终点及没有后续步骤的节点', () => {
    const s = useWorkflowStore()
    s.name = ' '
    expect(() => s.save()).toThrow('名称')
    s.name = '流程'
    s.remove(3)
    expect(() => s.save()).toThrow('结束节点')
  })
})
describe('业务引用与演示身份', () => {
  it('数字员工只引用清单内 Agent', () => {
    expect(new Set(agents.map((a) => a.id)).size).toBe(4)
    for (const e of employees)
      for (const id of e.agentIds) expect(agents.some((a) => a.id === id)).toBe(true)
  })
  it('演示登录不能成为真实认证，退出清理状态', () => {
    const user = useUserStore()
    user.enterDemo('访客')
    expect(user.demoSession).toBe(true)
    expect(user.authenticated).toBe(false)
    user.logout()
    expect(user.demoSession).toBe(false)
    expect(user.permissions).toEqual([])
  })
})
