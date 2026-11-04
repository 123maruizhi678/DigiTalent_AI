<script setup lang="ts">
import { agentName } from '@/config/agents'
import ModuleWorkspace from '@/components/business/ModuleWorkspace.vue'
import { ref } from 'vue'
import { useLocalActions } from '@/utils/localActions'
import ActionDialog from '@/components/business/ActionDialog.vue'
import DemoTable from '@/components/business/DemoTable.vue'
const actions = useLocalActions()
const tab = ref('t-user')
const tables = [
  {
    columns: ['姓名', '部门', '角色', '数据权限范围', '状态', '操作'],
    rows: [
      ['系统管理员 admin@corp.com', '信息技术部', '超级管理员', '全集团 · 全字段', '正常', '编辑'],
      ['张 * 敏 zhangm@corp.com', '人力资源部', 'HR 管理员', '本部门 · 薪资脱敏', '正常', '编辑'],
      [
        '刘 * 强 liuq@corp.com',
        'AI 平台事业部',
        '业务负责人',
        '本事业部 · 部分字段',
        '正常',
        '编辑',
      ],
      ['陈 * 宇 cheny@corp.com', 'AI 平台事业部', '普通员工', '仅本人数据', '正常', '编辑'],
      ['吴 * 涛 wut@corp.com', '数据智能部', '普通员工', '仅本人数据', '已停用', '编辑'],
    ],
  },
  {
    columns: ['时间', '操作人', '操作类型', '对象', '结果'],
    rows: [
      ['2026-09-27 14:32', '张 * 敏', '批量导出简历', '高级算法工程师 · 42 份', '成功'],
      ['2026-09-27 14:18', '系统', 'AI 调用', agentName('job-matcher') + ' · 批次 #2486', '成功'],
      ['2026-09-27 13:56', '吴 * 涛', '越权访问', '薪酬带宽表', '已拦截'],
      ['2026-09-27 11:20', '刘 * 强', '智能问数', '本事业部招聘完成率', '成功'],
      ['2026-09-27 10:04', '系统管理员', '修改角色权限', 'HR 管理员 · 字段级', '成功'],
    ],
  },
]
</script>
<template>
  <section class="page active">
    <div class="page-head">
      <div>
        <h1>系统管理</h1>
        <p>
          账号由后台创建或邀请；角色与权限为本地配置演示，后端身份、数据范围校验及操作审计待接入。
        </p>
        <p>用户 / 部门 / 角色 / 菜单 / 日志 · 精细化多级权限（角色 · 行级 · 字段级）</p>
      </div>
      <div class="head-actions">
        <el-button class="btn" @click="actions.open('操作日志')">操作日志</el-button>
        <el-button class="btn primary" @click="actions.open('+ 新增用户')">+ 新增用户</el-button>
      </div>
    </div>

    <div class="tabs">
      <div class="tab" :class="{ on: tab === 't-user' }" @click="tab = 't-user'">用户管理</div>
      <div class="tab" :class="{ on: tab === 't-role' }" @click="tab = 't-role'">角色与权限</div>
      <div class="tab" :class="{ on: tab === 't-log' }" @click="tab = 't-log'">审计日志</div>
    </div>

    <div v-show="tab === 't-user'" class="tab-panel on">
      <div class="card" style="padding: 0; overflow: hidden">
        <DemoTable :data="tables[0]" @action="actions.open" />
      </div>
    </div>

    <div v-show="tab === 't-role'" class="tab-panel on">
      <div class="grid-3">
        <div class="card">
          <div class="card-head">
            <h3>角色：HR 管理员</h3>
            <span class="tag blue">12 人</span>
          </div>
          <div class="kpi-line">
            <span class="k">功能权限</span><span class="v">简历 / 岗位 / 测评 </span>
          </div>
          <div class="kpi-line">
            <span class="k">行级权限</span><span class="tag ok">本部门及下级</span>
          </div>
          <div class="kpi-line">
            <span class="k">字段级权限</span><span class="tag warn">薪资字段脱敏</span>
          </div>
          <div class="kpi-line">
            <span class="k">数据导出</span><span class="tag ok">允许（含水印）</span>
          </div>
        </div>
        <div class="card">
          <div class="card-head">
            <h3>角色：业务负责人</h3>
            <span class="tag cyan">36 人</span>
          </div>
          <div class="kpi-line">
            <span class="k">功能权限</span><span class="v">岗位匹配 / 缺口 </span>
          </div>
          <div class="kpi-line">
            <span class="k">行级权限</span><span class="tag ok">本事业部</span>
          </div>
          <div class="kpi-line">
            <span class="k">字段级权限</span><span class="tag warn">联系方式脱敏</span>
          </div>
          <div class="kpi-line">
            <span class="k">数据导出</span><span class="tag warn">需审批</span>
          </div>
        </div>
        <div class="card">
          <div class="card-head">
            <h3>角色：普通员工</h3>
            <span class="tag gray">8,420 人</span>
          </div>
          <div class="kpi-line"><span class="k">功能权限</span><span class="v">测评</span></div>
          <div class="kpi-line">
            <span class="k">行级权限</span><span class="tag ok">仅本人</span>
          </div>
          <div class="kpi-line">
            <span class="k">字段级权限</span><span class="tag ok">全部脱敏</span>
          </div>
          <div class="kpi-line">
            <span class="k">数据导出</span><span class="tag danger">禁止</span>
          </div>
        </div>
      </div>
    </div>

    <div v-show="tab === 't-log'" class="tab-panel on">
      <div class="card" style="padding: 0; overflow: hidden">
        <DemoTable :data="tables[1]" @action="actions.open" />
      </div>
    </div>
    <ModuleWorkspace :sections="['组织管理', '权限管理']" /><ActionDialog :actions="actions" />
  </section>
</template>
