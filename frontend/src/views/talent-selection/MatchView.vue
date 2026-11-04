<script setup lang="ts">
import EvidencePanel from '@/components/business/EvidencePanel.vue'
import { ref } from 'vue'
import { useLocalActions } from '@/utils/localActions'
import ActionDialog from '@/components/business/ActionDialog.vue'
const actions = useLocalActions()
const chips = ref<string[]>([])
function toggle(value: string) {
  chips.value = chips.value.includes(value)
    ? chips.value.filter((x) => x !== value)
    : [...chips.value, value]
}
</script>
<template>
  <section class="page active">
    <div class="page-head">
      <div>
        <h1>岗位-人才精准匹配</h1>
        <p>岗位结构化解析 → 向量建模 · 0–100 匹配分 · 匹配原因可解释 · 岗位空缺预警与储备推荐</p>
      </div>
      <div class="head-actions">
        <el-button class="btn" @click="actions.open('岗位条件配置')">岗位条件配置</el-button>
        <el-button class="btn primary" @click="actions.open('+ 新建匹配任务')"
          >+ 新建匹配任务</el-button
        >
      </div>
    </div>

    <div class="card" style="margin-bottom: 14px">
      <div class="card-head">
        <h3>当前岗位：高级算法工程师（AI 平台部）</h3>
        <span class="tag danger">缺口 17 人</span>
      </div>
      <div class="chips">
        <button
          class="chip"
          :class="{ on: chips.includes('硕士及以上') }"
          @click="toggle('硕士及以上')"
        >
          硕士及以上
        </button>
        <button
          class="chip"
          :class="{ on: chips.includes('5 年以上') }"
          @click="toggle('5 年以上')"
        >
          5 年以上
        </button>
        <button
          class="chip"
          :class="{ on: chips.includes('LLM / RAG 经验') }"
          @click="toggle('LLM / RAG 经验')"
        >
          LLM / RAG 经验
        </button>
        <button class="chip" :class="{ on: chips.includes('PyTorch') }" @click="toggle('PyTorch')">
          PyTorch
        </button>
        <button
          class="chip"
          :class="{ on: chips.includes('分布式训练') }"
          @click="toggle('分布式训练')"
        >
          分布式训练
        </button>
        <button
          class="chip"
          :class="{ on: chips.includes('顶会论文优先') }"
          @click="toggle('顶会论文优先')"
        >
          顶会论文优先
        </button>
      </div>
    </div>

    <div class="grid-2">
      <div class="card">
        <div class="card-head">
          <h3>匹配结果（按匹配分排序）</h3>
          <span class="tag gray">共 42 位候选</span>
        </div>

        <div class="row">
          <div class="ring" style="--v: 94; --rc: #10b981"><span>94</span></div>
          <div class="grow">
            <div class="t1">陈 * 宇 · 硕士 · 6 年</div>
            <div class="t2">LLM 微调 / RAG / 分布式训练 · 完全命中核心要求</div>
          </div>
          <el-button class="btn sm" @click="actions.open('查看')">查看</el-button>
        </div>

        <div class="row">
          <div class="ring" style="--v: 91; --rc: #10b981"><span>91</span></div>
          <div class="grow">
            <div class="t1">赵 * 涵 · 博士 · 3 年</div>
            <div class="t2">多模态 / CV / 顶会 3 篇 · 经验年限略低</div>
          </div>
          <el-button class="btn sm" @click="actions.open('查看')">查看</el-button>
        </div>

        <div class="row">
          <div class="ring" style="--v: 85; --rc: #10b981"><span>85</span></div>
          <div class="grow">
            <div class="t1">孙 * 明 · 硕士 · 7 年</div>
            <div class="t2">推荐系统 / 特征工程 · RAG 经验较弱</div>
          </div>
          <el-button class="btn sm" @click="actions.open('查看')">查看</el-button>
        </div>

        <div class="row">
          <div class="ring" style="--v: 72; --rc: #f59e0b"><span>72</span></div>
          <div class="grow">
            <div class="t1">周 * 琳 · 本科 · 5 年</div>
            <div class="t2">后端开发 / 高并发 · 算法经验不足</div>
          </div>
          <el-button class="btn sm" @click="actions.open('查看')">查看</el-button>
        </div>

        <div class="row">
          <div class="ring" style="--v: 64; --rc: #f59e0b"><span>64</span></div>
          <div class="grow">
            <div class="t1">吴 * 涛 · 硕士 · 4 年</div>
            <div class="t2">数据分析 / SQL · 岗位方向差异较大</div>
          </div>
          <el-button class="btn sm" @click="actions.open('查看')">查看</el-button>
        </div>
      </div>

      <div style="display: flex; flex-direction: column; gap: 14px">
        <div class="card">
          <div class="card-head">
            <h3>匹配原因可解释</h3>
            <span class="tag blue">陈 * 宇 · 94 分</span>
          </div>
          <div class="kpi-line">
            <span class="k">技术栈匹配度</span
            ><span class="v" style="color: var(--ok)">96 / 100</span>
          </div>
          <div class="kpi-line">
            <span class="k">经验年限匹配</span
            ><span class="v" style="color: var(--ok)">92 / 100</span>
          </div>
          <div class="kpi-line">
            <span class="k">学历匹配</span><span class="v" style="color: var(--ok)">100 / 100</span>
          </div>
          <div class="kpi-line">
            <span class="k">行业背景匹配</span
            ><span class="v" style="color: var(--warn)">81 / 100</span>
          </div>
          <div class="kpi-line"><span class="k">稳定性预测</span><span class="v">良好</span></div>
          <div class="empty-note">
            命中：LLM 微调（LoRA/QLoRA）、RAG 架构、vLLM 推理优化、分布式训练<br />
            缺口：缺少推荐系统与搜索排序经验（占比 8%）
          </div>
        </div>

        <div class="card">
          <div class="card-head"><h3>岗位空缺预警 &amp; 储备推荐</h3></div>
          <div class="kpi-line">
            <span class="k">空缺岗位数</span><span class="v" style="color: var(--danger)">17</span>
          </div>
          <div class="kpi-line">
            <span class="k">自动推荐储备人才</span><span class="v">24 人</span>
          </div>
          <div class="kpi-line">
            <span class="k">已发出面试邀约</span><span class="v">9 人</span>
          </div>
          <div class="kpi-line">
            <span class="k">预计闭环周期</span><span class="v">18 天</span>
          </div>
        </div>
      </div>
    </div>
    <ActionDialog :actions="actions" />
    <EvidencePanel mode="match" />
  </section>
</template>
