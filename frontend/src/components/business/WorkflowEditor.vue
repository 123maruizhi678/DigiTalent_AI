<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useWorkflowStore, nodeTypes } from '@/stores/modules/workflow'
import { agents, agentName } from '@/config/agents'
const store = useWorkflowStore(),
  selected = ref(2),
  type = ref('Agent 节点')
const node = computed(() => store.nodes.find((n) => n.id === selected.value))
const edge = reactive({ source: 1, target: 2, condition: '' })
function add() {
  selected.value = store.add(type.value)
}
async function action(run = false) {
  try {
    if (run) await store.simulate()
    else {
      store.save()
      ElMessage.success('已保存至当前演示会话，刷新后重置')
    }
  } catch (error) {
    ElMessage.error((error as Error).message)
  }
}
function connect() {
  try {
    store.connect(edge)
  } catch (error) {
    ElMessage.error((error as Error).message)
  }
}
</script>
<template>
  <div class="card module-workspace">
    <div class="card-head">
      <h3>Workflow 画布 · 本地交互原型</h3>
      <div>
        <el-button :disabled="store.running" @click="action()">保存</el-button
        ><el-button type="primary" :loading="store.running" @click="action(true)"
          >模拟运行</el-button
        >
      </div>
    </div>
    <fieldset :disabled="store.running" class="workflow-fields">
      <el-form label-position="top"
        ><el-form-item label="工作流名称"
          ><el-input v-model="store.name" maxlength="80" /></el-form-item
        ><el-form-item label="工作流描述"><el-input v-model="store.description" /></el-form-item
      ></el-form>
      <div class="workspace-toolbar">
        <el-select v-model="type" aria-label="新增节点类型"
          ><el-option v-for="t in nodeTypes" :key="t" :value="t" /></el-select
        ><el-button @click="add">新增节点</el-button>
      </div>
      <div class="workflow-layout">
        <div>
          <div class="workflow-canvas">
            <button
              v-for="n in store.nodes"
              :key="n.id"
              class="workflow-node"
              :class="{ selected: n.id === selected }"
              @click="selected = n.id"
            >
              <b>{{ n.id }} · {{ n.type === 'Agent 节点' ? agentName(n.agentId) : n.name }}</b
              ><small>{{ n.type }}</small>
            </button>
          </div>
          <p class="empty-note">点击节点编辑；连线在下方配置。当前采用列表式画布，不支持拖拽。</p>
        </div>
        <el-form v-if="node" label-position="top" class="card"
          ><h3>节点信息 #{{ node.id }}</h3>
          <el-form-item label="节点名称"><el-input v-model="node.name" /></el-form-item
          ><el-form-item label="节点类型"
            ><el-select v-model="node.type"
              ><el-option v-for="t in nodeTypes" :key="t" :value="t" /></el-select></el-form-item
          ><el-form-item v-if="node.type === 'Agent 节点'" label="调用 Agent"
            ><el-select v-model="node.agentId"
              ><el-option
                v-for="a in agents"
                :key="a.id"
                :value="a.id"
                :label="a.name" /></el-select></el-form-item
          ><el-form-item label="输入 / 工具参数 / 审核说明"
            ><el-input v-model="node.config" type="textarea" /></el-form-item
          ><el-button type="danger" @click="store.remove(node!.id)"
            >删除节点及关联连线</el-button
          ></el-form
        >
      </div>
      <h3>节点连接与连线配置</h3>
      <div class="workflow-connections">
        <el-select v-model="edge.source" aria-label="起点"
          ><el-option
            v-for="n in store.nodes"
            :key="n.id"
            :value="n.id"
            :label="n.id + ' · ' + n.name" /></el-select
        ><span>→</span
        ><el-select v-model="edge.target" aria-label="终点"
          ><el-option
            v-for="n in store.nodes"
            :key="n.id"
            :value="n.id"
            :label="n.id + ' · ' + n.name" /></el-select
        ><el-input v-model="edge.condition" placeholder="分支条件（仅配置，不求值）" /><el-button
          @click="connect"
          >添加连线</el-button
        >
      </div>
      <div v-for="(e, i) in store.edges" :key="e.source + '-' + e.target" class="kpi-line">
        <span>#{{ e.source }} → #{{ e.target }} · {{ e.condition || '默认' }}</span
        ><el-button size="small" @click="store.edges.splice(i, 1)">删除连线</el-button>
      </div>
    </fieldset>
    <p class="empty-note">
      {{ store.saved ? '已有当前会话保存快照' : '尚未保存' }} · 配置变更后需重新保存
    </p>
    <h3>模拟执行记录与结果</h3>
    <p v-if="!store.logs.length" class="empty-note">尚未模拟运行</p>
    <p v-for="(log, i) in store.logs" :key="i" class="empty-note">{{ log }}</p>
  </div>
</template>
<style scoped>
.workflow-fields {
  border: 0;
  padding: 0;
  min-width: 0;
}
.workflow-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  gap: 16px;
}
.workflow-canvas {
  display: flex;
  flex-wrap: wrap;
  gap: 18px;
  padding: 24px;
  background: #f4f6ff;
  border-radius: 12px;
  min-height: 220px;
  align-content: flex-start;
}
.workflow-node {
  background: white;
  border: 1px solid #c4cde0;
  border-radius: 10px;
  padding: 16px;
  cursor: pointer;
  color: #273451;
}
.workflow-node.selected {
  border: 2px solid #7560db;
}
.workflow-node small {
  display: block;
  margin-top: 8px;
}
.workflow-connections {
  display: flex;
  gap: 10px;
  margin: 14px 0;
  flex-wrap: wrap;
}
.workflow-connections .el-select {
  width: 180px;
}
.workflow-connections .el-input {
  width: 230px;
}
@media (max-width: 1100px) {
  .workflow-layout {
    grid-template-columns: 1fr;
  }
}
</style>
