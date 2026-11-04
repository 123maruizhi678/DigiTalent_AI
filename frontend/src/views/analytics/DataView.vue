<script setup lang="ts">
import ModuleWorkspace from '@/components/business/ModuleWorkspace.vue'
import { useLocalActions } from '@/utils/localActions'
import ActionDialog from '@/components/business/ActionDialog.vue'
import BusinessChart from '@/components/charts/BusinessChart.vue'
import DemoTable from '@/components/business/DemoTable.vue'
const actions = useLocalActions()
const tables = [
  {
    columns: ['事业部', '招聘完成率', '测评平均得分', '人才缺口'],
    rows: [
      ['AI 平台事业部', '94.1%', '14.2 分', '17 人'],
      ['云服务事业部', '86.3%', '12.8 分', '8 人'],
      ['数字金融事业部', '81.2%', '11.6 分', '6 人'],
      ['智慧城市事业部', '74.5%', '10.4 分', '3 人'],
      ['智能制造事业部', '68.3%', '9.1 分', '2 人'],
    ],
  },
]
</script>
<template>
  <section class="page active">
    <div class="page-head">
      <div>
        <h1>自然语言智能数据决策</h1>
        <p>口语化自由问数 · 自动多维分析 · 自动出图 · 导出本地演示报告 · 行/字段级权限联动</p>
      </div>
      <div class="head-actions">
        <el-button class="btn" @click="actions.open('导出数据')">导出数据</el-button>
        <el-button class="btn primary" @click="actions.open('导出报告')">导出报告</el-button>
      </div>
    </div>

    <div class="card" style="margin-bottom: 14px">
      <div class="chat">
        <div class="msg user">
          <div class="msg-av">我</div>
          <div class="bubble">统计近 6 个月各事业部的招聘完成率与测评平均得分，做个对比</div>
        </div>

        <div class="msg">
          <div class="msg-av">AI</div>
          <div class="bubble">
            <b>模拟分析结果。</b>近 6 个月集团整体招聘完成率 82.4%，其中 <b>AI 平台事业部</b> 以
            94.1% 领先，<b>智能制造事业部</b> 最低（68.3%）；测评平均得分整体呈上升趋势，9 月达到
            78.4 分 / 人。
            <div class="cite">
              <span class="n">SQL</span>原型固定分析结果 · 未执行 SQL · 权限范围：全集团（行级）·
              耗时 1.8s
            </div>
          </div>
        </div>
      </div>

      <div class="grid-2 even" style="margin-top: 18px">
        <div>
          <div style="font-size: 13px; font-weight: 700; margin-bottom: 12px">
            各事业部招聘完成率（%）
          </div>
          <BusinessChart
            kind="bar"
            :values="[94, 86, 81, 74, 68]"
            :labels="['AI 平台', '云服务', '数字金融', '智慧城市', '智能制造']"
          />
        </div>
        <div>
          <div style="font-size: 13px; font-weight: 700; margin-bottom: 12px">
            测评平均得分趋势（分）
          </div>
          <BusinessChart
            kind="bar"
            :values="[52, 60, 57, 72, 83, 92]"
            :labels="['4月', '5月', '6月', '7月', '8月', '9月']"
          />
        </div>
      </div>
    </div>

    <div class="grid-2">
      <div class="card" style="padding: 0; overflow: hidden">
        <DemoTable :data="tables[0]" @action="actions.open" />
      </div>

      <div style="display: flex; flex-direction: column; gap: 14px">
        <div class="card">
          <div class="card-head">
            <h3>智能决策建议</h3>
            <span class="tag violet">模拟结果</span>
          </div>
          <div class="kpi-line">
            <span class="k">建议 1</span
            ><span class="v" style="text-align: right; font-weight: 500; font-size: 12.5px"
              >智能制造事业部招聘周期偏长，建议放宽学历硬条件</span
            >
          </div>
          <div class="kpi-line">
            <span class="k">建议 2</span
            ><span class="v" style="text-align: right; font-weight: 500; font-size: 12.5px"
              >AI 平台事业部缺口最大，建议启用储备人才池直招</span
            >
          </div>
          <div class="kpi-line">
            <span class="k">建议 3</span
            ><span class="v" style="text-align: right; font-weight: 500; font-size: 12.5px"
              >测评分数与招聘完成率正相关，建议加大测评覆盖</span
            >
          </div>
        </div>

        <div class="card">
          <div class="card-head">
            <h3>权限与合规</h3>
            <span class="tag ok">已校验</span>
          </div>
          <div class="kpi-line">
            <span class="k">当前角色</span><span class="v">管理层 · 全集团</span>
          </div>
          <div class="kpi-line">
            <span class="k">行级权限</span><span class="tag gray">后端待接入</span>
          </div>
          <div class="kpi-line">
            <span class="k">字段级脱敏</span><span class="tag ok">薪资字段已屏蔽</span>
          </div>
          <div class="kpi-line">
            <span class="k">查询留痕</span><span class="tag ok">演示审计快照</span>
          </div>
        </div>
      </div>
    </div>

    <div class="ask-bar" style="margin-top: 14px">
      <input
        v-model="actions.question.value"
        placeholder="用自然语言继续追问，例如：对比一下各事业部的离职率…"
      />
      <el-button class="btn primary" @click="actions.open('发送')">发送</el-button>
    </div>
    <ModuleWorkspace
      :sections="['数据统计', '人才分析', '招聘分析', '测评分析', '运营数据', '决策驾驶舱']"
    /><ActionDialog :actions="actions" />
  </section>
</template>
