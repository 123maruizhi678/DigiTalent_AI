<script setup lang="ts">
import { technologies, services, technicalStatuses, technicalTodos } from '@/config/technology'
</script>
<template>
  <section class="page active">
    <div class="page-head">
      <div>
        <h1>系统技术状态与服务监控</h1>
        <p>技术方案与实际运行状态分别记录；尚未接入监控接口</p>
      </div>
    </div>
    <div class="card">
      <h3>技术组件清单</h3>
      <el-table :data="technologies"
        ><el-table-column prop="category" label="类别" min-width="140" /><el-table-column
          prop="name"
          label="组件"
          min-width="240" /><el-table-column prop="status" label="技术状态" /><el-table-column
          prop="deployment"
          label="部署方式"
          min-width="180"
      /></el-table>
    </div>
    <div class="card module-workspace">
      <h3>服务状态 · 未连接真实监控</h3>
      <el-table :data="services"
        ><el-table-column
          v-for="[prop, label] in [
            ['name', '服务名称'],
            ['address', '服务地址'],
            ['status', '当前状态'],
            ['deployment', '部署方式'],
            ['version', '版本信息'],
            ['checkedAt', '最近检查时间'],
          ]"
          :key="prop"
          :prop="prop"
          :label="label"
          min-width="150"
      /></el-table>
    </div>
    <div class="grid-2 module-workspace">
      <div class="card">
        <h3>技术状态分类</h3>
        <p v-for="(meaning, status) in technicalStatuses" :key="status" class="empty-note">
          <b>{{ status }}</b
          >：{{ meaning }}
        </p>
      </div>
      <div class="card">
        <h3>技术风险与待办事项</h3>
        <p v-for="todo in technicalTodos" :key="todo" class="empty-note">{{ todo }}</p>
      </div>
    </div>
  </section>
</template>
