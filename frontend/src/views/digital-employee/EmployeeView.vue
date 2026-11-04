<script setup lang="ts">
import ModuleWorkspace from '@/components/business/ModuleWorkspace.vue'
import { ref } from 'vue'
import BusinessChart from '@/components/charts/BusinessChart.vue'
import DemoTable from '@/components/business/DemoTable.vue'
import ActionDialog from '@/components/business/ActionDialog.vue'
import { useLocalActions } from '@/utils/localActions'
import { employees, agentName } from '@/config/agents'
const actions = useLocalActions(),
  tab = ref('employees')
const tables = {
  employees: {
    columns: ['数字员工', '角色 / 职责', '能力', '状态', '操作'],
    rows: employees.map((e) => [
      e.name,
      e.role,
      e.agentIds.map(agentName).join(' / '),
      '待执行（模拟）',
      '配置能力',
    ]),
  },
  tasks: {
    columns: [
      '任务名称',
      '任务类型',
      '任务来源',
      '执行对象',
      '执行状态',
      '执行时间',
      '执行结果',
      '异常信息',
      '操作',
    ],
    rows: [
      [
        '每日简历整理',
        '档案整理',
        '定时',
        '简历助手',
        '排队（模拟）',
        '每日 09:00',
        '待执行',
        '无',
        '配置调度',
      ],
      [
        '招聘统计',
        '统计报告',
        '手动',
        '数据助手',
        '完成（模拟）',
        '示例 09:10',
        '模拟报告',
        '无',
        '查看记录',
      ],
      [
        '测评提醒',
        '招聘协作',
        '事件触发',
        '招聘助手',
        '失败（模拟）',
        '示例 10:00',
        '未发送',
        '模拟超时',
        '重试',
      ],
    ],
  },
}
</script>
<template>
  <section class="page active">
    <div class="page-head">
      <div>
        <h1>数字员工与任务调度</h1>
        <p>数字员工拥有角色与 Agent 能力，可参与 Workflow；任务记录执行对象、来源和结果</p>
      </div>
      <el-button type="primary" @click="actions.open('新建任务')">+ 新建任务</el-button>
    </div>
    <div class="stat-grid">
      <div
        v-for="[label, value] in [
          ['数字员工', String(employees.length)],
          ['排队任务', '14'],
          ['执行中', '6'],
          ['今日完成', '2,486'],
        ]"
        :key="label"
        class="card stat"
      >
        <div class="stat-label">{{ label }}</div>
        <div class="stat-num">{{ value }}</div>
      </div>
    </div>
    <el-tabs v-model="tab"
      ><el-tab-pane label="数字员工管理" name="employees" /><el-tab-pane
        label="任务与调度"
        name="tasks"
    /></el-tabs>
    <div class="card">
      <DemoTable
        :key="tab"
        :data="tab === 'employees' ? tables.employees : tables.tasks"
        @action="actions.open"
      />
    </div>
    <div class="grid-2 even" style="margin-top: 14px">
      <div class="card">
        <h3>近七日任务执行量</h3>
        <BusinessChart
          kind="line"
          :labels="['周一', '周二', '周三', '周四', '周五', '周六', '周日']"
          :values="[286, 310, 280, 428, 386, 260, 310]"
        />
      </div>
      <div class="card">
        <h3>执行状态分布</h3>
        <BusinessChart
          kind="pie"
          :labels="['完成', '执行中', '排队', '失败']"
          :values="[86, 6, 14, 3]"
        />
      </div>
    </div>
    <ModuleWorkspace
      :sections="['员工能力配置', '任务管理', '任务调度', '执行记录', '执行状态监控']"
    /><ActionDialog :actions="actions" />
  </section>
</template>
