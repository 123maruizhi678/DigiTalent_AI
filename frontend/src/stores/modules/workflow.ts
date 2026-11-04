import { defineStore } from 'pinia'
import { agents, type AgentId } from '@/config/agents'
export const nodeTypes = [
  '开始节点',
  '结束节点',
  'Agent 节点',
  '工具节点',
  '条件判断节点',
  '人工审核节点',
] as const
export interface FlowNode {
  id: number
  type: string
  name: string
  agentId: AgentId
  config: string
}
export interface FlowEdge {
  source: number
  target: number
  condition: string
}
export const useWorkflowStore = defineStore('workflow', {
  state: () => ({
    name: '招聘筛选流程',
    description: '简历解析后人工复核',
    nextId: 4,
    nodes: [
      { id: 1, type: '开始节点', name: '简历上传', agentId: agents[0].id, config: '' },
      { id: 2, type: 'Agent 节点', name: '解析', agentId: agents[0].id, config: '提取技能与经历' },
      { id: 3, type: '结束节点', name: '输出结果', agentId: agents[0].id, config: '' },
    ] as FlowNode[],
    edges: [
      { source: 1, target: 2, condition: '' },
      { source: 2, target: 3, condition: '' },
    ] as FlowEdge[],
    saved: '',
    logs: [] as string[],
    running: false,
  }),
  actions: {
    add(type: string) {
      const node = { id: this.nextId++, type, name: type, agentId: agents[0].id, config: '' }
      this.nodes.push(node)
      return node.id
    },
    remove(id: number) {
      this.nodes = this.nodes.filter((n) => n.id !== id)
      this.edges = this.edges.filter((e) => e.source !== id && e.target !== id)
    },
    connect(edge: FlowEdge) {
      if (
        edge.source === edge.target ||
        !this.nodes.some((n) => n.id === edge.source) ||
        !this.nodes.some((n) => n.id === edge.target)
      )
        throw Error('请选择不同且存在的节点')
      if (this.edges.some((e) => e.source === edge.source && e.target === edge.target))
        throw Error('连线已存在')
      this.edges.push({ ...edge })
    },
    validate() {
      if (!this.name.trim() || this.nodes.some((n) => !n.name.trim()))
        throw Error('工作流和节点名称不能为空')
      if (
        this.nodes.filter((n) => n.type === '开始节点').length !== 1 ||
        !this.nodes.some((n) => n.type === '结束节点')
      )
        throw Error('需要一个开始节点和至少一个结束节点')
      const visited = new Set<number>(),
        active = new Set<number>()
      const walk = (id: number) => {
        if (active.has(id)) throw Error('模拟仅支持无环流程')
        if (visited.has(id)) return
        active.add(id)
        for (const e of this.edges.filter((e) => e.source === id)) walk(e.target)
        active.delete(id)
        visited.add(id)
      }
      walk(this.nodes.find((n) => n.type === '开始节点')!.id)
      if (visited.size !== this.nodes.length) throw Error('存在未连接到开始节点的节点')
      if (
        this.nodes.some((n) => n.type !== '结束节点' && !this.edges.some((e) => e.source === n.id))
      )
        throw Error('非结束节点需要后续连线')
      if (
        this.nodes.some((n) => n.type === '结束节点' && this.edges.some((e) => e.source === n.id))
      )
        throw Error('结束节点不能连接后续节点')
    },
    save() {
      this.validate()
      this.saved = JSON.stringify({
        name: this.name,
        description: this.description,
        nodes: this.nodes,
        edges: this.edges,
      })
    },
    async simulate() {
      this.validate()
      this.running = true
      this.logs = ['模拟开始：仅演示拓扑顺序，不执行条件、工具或人工审核']
      try {
        const pending = [...this.nodes],
          done = new Set<number>()
        while (pending.length) {
          const index = pending.findIndex((n) =>
            this.edges.filter((e) => e.target === n.id).every((e) => done.has(e.source)),
          )
          const node = pending.splice(index, 1)[0]!
          this.logs.push(`${node.name}：模拟执行中`)
          await new Promise((resolve) => setTimeout(resolve, 150))
          this.logs.push(
            `${node.name}：模拟完成${node.type === '人工审核节点' ? '（未进行真实人工审批）' : ''}`,
          )
          done.add(node.id)
        }
        this.logs.push('模拟结果：流程结构可遍历，未生成真实业务结果')
      } finally {
        this.running = false
      }
    },
  },
})
