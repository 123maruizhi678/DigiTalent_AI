<script setup lang="ts">
import EvidencePanel from '@/components/business/EvidencePanel.vue'
import OnlineAssessment from '@/components/business/OnlineAssessment.vue'
import ModuleWorkspace from '@/components/business/ModuleWorkspace.vue'
import { useLocalActions } from '@/utils/localActions'
import ActionDialog from '@/components/business/ActionDialog.vue'
import BusinessChart from '@/components/charts/BusinessChart.vue'
import DemoTable from '@/components/business/DemoTable.vue'
const actions = useLocalActions()
const tables = [
  {
    columns: ['考生', '试卷', '得分', '能力评级', '状态'],
    rows: [
      ['陈 * 宇', '高级算法 · A 卷', '94', 'A+ 优秀', '已完成'],
      ['李 * 婷', '数据分析 · B 卷', '88', 'A 良好', '已完成'],
      ['王 * 峰', 'AI 产品 · A 卷', '71', 'B 待提升', '已完成'],
      ['赵 * 涵', '高级算法 · C 卷', '—', '待研判', '考试中 42%'],
    ],
  },
]
</script>
<template>
  <section class="page active">
    <div class="page-head">
      <div>
        <h1>智能测评</h1>
        <p>大模型自适应题库（千人千卷）· 全流程自动调度 · AI 能力结构分析 · 动态能力评级</p>
      </div>
      <div class="head-actions">
        <el-button class="btn" @click="actions.open('题库管理')">题库管理</el-button>
        <el-button class="btn primary" @click="actions.open('+ 智能出卷')">+ 智能出卷</el-button>
      </div>
    </div>

    <div class="stat-grid">
      <div class="card stat">
        <div class="stat-label"><i class="dot blue"></i>题库总量</div>
        <div class="stat-num">18,420<span class="unit">题</span></div>
        <div class="stat-foot">覆盖 26 个技术方向</div>
      </div>
      <div class="card stat">
        <div class="stat-label"><i class="dot cyan"></i>本月生成试卷</div>
        <div class="stat-num">1,086<span class="unit">套</span></div>
        <div class="stat-foot up">千人千卷 100% 生效</div>
      </div>
      <div class="card stat">
        <div class="stat-label"><i class="dot amber"></i>平均分</div>
        <div class="stat-num">78.4<span class="unit">分</span></div>
        <div class="stat-foot up">↑ 3.1 分 环比</div>
      </div>
      <div class="card stat">
        <div class="stat-label"><i class="dot violet"></i>错题复盘覆盖率</div>
        <div class="stat-num">92<span class="unit">%</span></div>
        <div class="stat-foot">已生成复习计划 1,204 份</div>
      </div>
    </div>

    <div class="grid-2">
      <div class="card">
        <div class="card-head">
          <h3>近期考核成绩</h3>
          <span class="tag gray">自动研判</span>
        </div>
        <DemoTable :data="tables[0]" @action="actions.open" />
        <div class="empty-note">※ 系统按答题轨迹动态调节后续题目难度，实现"千人千卷"。</div>
      </div>

      <div class="card">
        <div class="card-head">
          <h3>能力结构分析 · 陈 * 宇</h3>
          <span class="tag blue">动态评级 A+</span>
        </div>
        <BusinessChart kind="radar" />
        <div class="kpi-line">
          <span class="k">优势项</span
          ><span class="v" style="color: var(--ok)">算法理论 · 工程落地</span>
        </div>
        <div class="kpi-line">
          <span class="k">待补强项</span><span class="v" style="color: var(--warn)">业务抽象</span>
        </div>
        <div class="kpi-line">
          <span class="k">建议复核能力</span><span class="v">业务建模能力待复核</span>
        </div>
      </div>
    </div>

    <div class="grid-3">
      <div class="card">
        <div class="card-head"><h3>智能出卷配置</h3></div>
        <div class="kpi-line">
          <span class="k">目标岗位</span><span class="v">高级算法工程师</span>
        </div>
        <div class="kpi-line">
          <span class="k">难度分布</span><span class="v">易 30% / 中 50% / 难 20%</span>
        </div>
        <div class="kpi-line">
          <span class="k">题量</span><span class="v">40 题 · 90 分钟</span>
        </div>
        <div class="kpi-line">
          <span class="k">自适应难度</span><span class="tag ok">已开启</span>
        </div>
      </div>
      <div class="card">
        <div class="card-head">
          <h3>AI 面试间</h3>
          <span class="tag violet">进行中 6 场</span>
        </div>
        <div class="kpi-line"><span class="k">今日排期</span><span class="v">24 场</span></div>
        <div class="kpi-line"><span class="k">平均时长</span><span class="v">32 分钟</span></div>
        <div class="kpi-line">
          <span class="k">面试评价生成</span><span class="tag ok">自动</span>
        </div>
      </div>
      <div class="card">
        <div class="card-head">
          <h3>错题复盘</h3>
          <span class="tag warn">Top 3 薄弱点</span>
        </div>
        <div class="kpi-line">
          <span class="k">分布式训练调优</span><span class="v">错误率 46%</span>
        </div>
        <div class="kpi-line">
          <span class="k">向量检索召回</span><span class="v">错误率 38%</span>
        </div>
        <div class="kpi-line">
          <span class="k">Prompt 工程</span><span class="v">错误率 31%</span>
        </div>
      </div>
    </div>
    <OnlineAssessment /><ModuleWorkspace
      :sections="['题库管理', '测评任务', '面试管理', '面试评价', '测评结果分析']"
    /><ActionDialog :actions="actions" />
    <EvidencePanel mode="exam" />
  </section>
</template>
