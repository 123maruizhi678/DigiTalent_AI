<script setup lang="ts">
import AgentCatalog from '@/components/business/AgentCatalog.vue'
import WorkflowEditor from '@/components/business/WorkflowEditor.vue'
import ModuleWorkspace from '@/components/business/ModuleWorkspace.vue'
</script>
<template>
  <section class="page active">
    <div class="page-head">
      <div>
        <h1>Agent 编排中心</h1>
        <p>统一 Agent 能力配置 · Workflow 节点与执行步骤管理 · 本地模拟</p>
      </div>
      <router-link to="/employee">数字员工与任务调度</router-link>
    </div>
    <AgentCatalog />
    <div class="card module-workspace">
      <h3>业务对象关系</h3>
      <p class="empty-note">
        Agent 提供特定能力；Workflow 管理节点、连接、顺序及分支；数字员工拥有角色与能力配置，可调用
        Agent 或参与 Workflow；任务是交给数字员工或 Workflow 执行的具体工作。
      </p>
    </div>
    <WorkflowEditor /><ModuleWorkspace :sections="['Prompt 管理', 'Tools 管理']" />
  </section>
</template>
