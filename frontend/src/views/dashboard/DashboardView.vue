<script setup lang="ts">
import { useLocalActions } from '@/utils/localActions'
import ActionDialog from '@/components/business/ActionDialog.vue'
import BusinessChart from '@/components/charts/BusinessChart.vue'
import AgentCatalog from '@/components/business/AgentCatalog.vue'
import { agents } from '@/config/agents'
import { services } from '@/config/technology'
const actions = useLocalActions()
</script>
<template>
  <section class="page active">
    <div class="card welcome">
      <h2>欢迎回来，系统管理员</h2>
      <p>从人才发现到智能协作，开启今天的工作。</p>
    </div>
    <div class="page-head">
      <div>
        <h1>智能工作台</h1>
        <p>AI 原生人才智能平台 · 全流程智能化运营概览（数据截至 2026-09-27）</p>
      </div>
      <div class="head-actions">
        <el-button class="btn" @click="actions.open('导出日报')">导出日报</el-button>
        <el-button class="btn primary" @click="actions.open('+ 发起 AI 任务')"
          >+ 发起 AI 任务</el-button
        >
      </div>
    </div>

    <div class="stat-grid">
      <div class="card stat">
        <div class="stat-label"><i class="dot blue"></i>在库人才档案</div>
        <div class="stat-num">12,486<span class="unit">人</span></div>
        <div class="stat-foot up">↑ 8.2% 环比上月</div>
      </div>
      <div class="card stat">
        <div class="stat-label"><i class="dot cyan"></i>本月解析简历</div>
        <div class="stat-num">3,254<span class="unit">份</span></div>
        <div class="stat-foot up">解析成功率 99.2%</div>
      </div>
      <div class="card stat">
        <div class="stat-label"><i class="dot amber"></i>待处理匹配任务</div>
        <div class="stat-num">86<span class="unit">项</span></div>
        <div class="stat-foot warn">12 项已超时预警</div>
      </div>
      <div class="card stat">
        <div class="stat-label"><i class="dot violet"></i>AI 调用量（本月）</div>
        <div class="stat-num">128.6<span class="unit">万次</span></div>
        <div class="stat-foot">覆盖 {{ agents.length }} 大 Agent · 模拟平均 412ms</div>
      </div>
    </div>

    <div class="grid-2">
      <div class="card">
        <div class="card-head">
          <h3>Agent 能力清单<span class="sub">统一能力配置</span></h3>
          <span class="tag gray">未连接</span>
        </div>

        <AgentCatalog compact />
      </div>

      <div class="card">
        <div class="card-head">
          <h3>人才缺口预警</h3>
          <span class="tag warn">3 条待处理</span>
        </div>

        <div class="row">
          <div class="ring" style="--v: 34; --rc: #ef4444"><span>34%</span></div>
          <div class="grow">
            <div class="t1">高级算法工程师</div>
            <div class="t2">需求 26 人 · 在库匹配 9 人 · 缺口 17 人</div>
          </div>
          <span class="tag danger">严重</span>
        </div>

        <div class="row">
          <div class="ring" style="--v: 61; --rc: #f59e0b"><span>61%</span></div>
          <div class="grow">
            <div class="t1">数据分析师（P6）</div>
            <div class="t2">需求 18 人 · 在库匹配 11 人 · 缺口 7 人</div>
          </div>
          <span class="tag warn">预警</span>
        </div>

        <div class="row">
          <div class="ring" style="--v: 76; --rc: #10b981"><span>76%</span></div>
          <div class="grow">
            <div class="t1">产品经理（AI 方向）</div>
            <div class="t2">需求 12 人 · 在库匹配 9 人 · 缺口 3 人</div>
          </div>
          <span class="tag ok">可控</span>
        </div>

        <div class="empty-note">※ 系统已自动向储备人才池推送 24 条岗位邀约，等待 HR 确认。</div>
      </div>
    </div>

    <div class="grid-3">
      <div class="card">
        <div class="card-head">
          <h3>简历解析吞吐</h3>
          <span class="tag gray">近 7 日</span>
        </div>
        <BusinessChart
          kind="bar"
          :values="[52, 68, 44, 81, 73, 95, 62]"
          :labels="['21', '22', '23', '24', '25', '26', '27']"
        />
      </div>

      <div class="card">
        <div class="card-head">
          <h3>测评任务分布</h3>
          <span class="tag gray">按角色</span>
        </div>
        <div class="kpi-line"><span class="k">普通员工</span><span class="v">4,812 次</span></div>
        <div class="kpi-line"><span class="k">HR / 招聘</span><span class="v">2,306 次</span></div>
        <div class="kpi-line"><span class="k">业务负责人</span><span class="v">1,184 次</span></div>
        <div class="kpi-line"><span class="k">管理层</span><span class="v">642 次</span></div>
        <div class="kpi-line">
          <span class="k">测评完成率</span><span class="v" style="color: var(--ok)">96.7%</span>
        </div>
      </div>

      <div class="card">
        <div class="card-head">
          <h3>系统健康度</h3>
          <span class="tag gray">待接入</span>
        </div>
        <div v-for="service in services" :key="service.name" class="kpi-line">
          <span class="k">{{ service.name }}</span
          ><span class="tag gray">{{ service.status }}</span>
        </div>
      </div>
    </div>
    <div class="grid-3">
      <div class="card">
        <h3>招聘流程转化</h3>
        <BusinessChart
          kind="funnel"
          :labels="['简历筛选', '测评', '面试', '录用']"
          :values="[428, 156, 86, 42]"
        />
      </div>
      <div class="card">
        <h3>测评完成率</h3>
        <BusinessChart kind="gauge" :values="[92]" />
      </div>
      <div class="card">
        <h3>任务执行情况</h3>
        <BusinessChart
          kind="pie"
          :labels="['已完成', '执行中', '排队', '失败']"
          :values="[86, 6, 14, 3]"
        />
      </div>
    </div>
    <ActionDialog :actions="actions" />
  </section>
</template>
