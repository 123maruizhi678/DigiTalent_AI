import { beforeEach, describe, expect, it } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useWorkspaceStore } from './workspace'
import { filterMenus, pageLoaders } from '@/router/routes'
beforeEach(() => setActivePinia(createPinia()))
describe('本地业务记录', () => {
  it('新增、编辑、执行和删除使用同一记录且互不影响其他模块', () => {
    const store = useWorkspaceStore()
    const initial = store.list('面试管理').length
    store.save('面试管理', null, { name: '技术复试', detail: '明日 14:00', status: '待执行' })
    const row = store.list('面试管理').at(-1)!
    expect(store.list('面试管理')).toHaveLength(initial + 1)
    store.save('面试管理', row.id, { name: '技术复试', detail: '明日 15:00', status: '待执行' })
    expect(row.detail).toBe('明日 15:00')
    store.status('面试管理', row.id, '已完成（模拟）')
    expect(row.status).toBe('已完成（模拟）')
    expect(store.list('组织管理')[0]!.name).toBe('AI 平台事业部')
    store.remove('面试管理', row.id)
    expect(store.list('面试管理')).toHaveLength(initial)
  })
  it('菜单覆盖七大模块且所有菜单拥有页面', () => {
    expect(filterMenus()).toHaveLength(8)
    for (const group of filterMenus())
      for (const [id] of group.items) expect(id! in pageLoaders).toBe(true)
    expect(filterMenus(['exam']).flatMap((g) => g.items)).toEqual([['exam', '智能测评与面试']])
    expect(filterMenus([])).toEqual([])
  })
})
