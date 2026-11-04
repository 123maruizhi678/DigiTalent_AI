<script setup lang="ts">
import EvidencePanel from '@/components/business/EvidencePanel.vue'
import ModuleWorkspace from '@/components/business/ModuleWorkspace.vue'
import { ref } from 'vue'
import { useLocalActions } from '@/utils/localActions'
import ActionDialog from '@/components/business/ActionDialog.vue'
import BusinessChart from '@/components/charts/BusinessChart.vue'
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
        <h1>人才画像档案</h1>
        <p>百级标签体系 · 语义化自然语言检索 · 单/批量档案 RAG 问答</p>
      </div>
      <div class="head-actions">
        <el-button class="btn" @click="actions.open('批量问答')">批量问答</el-button>
        <el-button class="btn primary" @click="actions.open('+ 新建档案')">+ 新建档案</el-button>
      </div>
    </div>

    <div class="grid-2">
      <div class="card">
        <div class="card-head">
          <h3>画像详情 · 陈 * 宇</h3>
          <span class="tag ok">档案完整度 96%</span>
        </div>

        <div style="display: flex; gap: 16px; align-items: center; margin-bottom: 18px">
          <div
            class="avatar"
            style="width: 56px; height: 56px; border-radius: 16px; font-size: 20px; flex: 0 0 56px"
          >
            陈
          </div>
          <div style="flex: 1">
            <div style="font-size: 16px; font-weight: 700">陈 * 宇</div>
            <div style="font-size: 12.5px; color: var(--ink3); margin-top: 5px">
              高级算法工程师 · 硕士 · 6 年经验 · 浙江大学
            </div>
            <div style="margin-top: 9px; display: flex; gap: 7px; flex-wrap: wrap">
              <span class="tag blue">LLM 微调</span>
              <span class="tag cyan">RAG 架构</span>
              <span class="tag violet">多模态</span>
              <span class="tag gray">团队协作</span>
            </div>
          </div>
        </div>

        <BusinessChart kind="radar" />

        <div class="chips" style="margin-top: 16px">
          <button
            class="chip"
            :class="{ on: chips.includes('全部标签 108') }"
            @click="toggle('全部标签 108')"
          >
            全部标签 108
          </button>
          <button
            class="chip"
            :class="{ on: chips.includes('技术栈 42') }"
            @click="toggle('技术栈 42')"
          >
            技术栈 42
          </button>
          <button
            class="chip"
            :class="{ on: chips.includes('项目经历 26') }"
            @click="toggle('项目经历 26')"
          >
            项目经历 26
          </button>
          <button
            class="chip"
            :class="{ on: chips.includes('软素质 21') }"
            @click="toggle('软素质 21')"
          >
            软素质 21
          </button>
          <button
            class="chip"
            :class="{ on: chips.includes('证书 19') }"
            @click="toggle('证书 19')"
          >
            证书 19
          </button>
        </div>
      </div>

      <div style="display: flex; flex-direction: column; gap: 14px">
        <div class="card">
          <div class="card-head">
            <h3>档案 RAG 问答</h3>
            <span class="tag cyan">可溯源</span>
          </div>
          <div class="chat">
            <div class="msg user">
              <div class="msg-av">我</div>
              <div class="bubble">这位候选人是否有大规模模型落地的完整经验？</div>
            </div>
            <div class="msg">
              <div class="msg-av">AI</div>
              <div class="bubble">
                <b>结论：具备。</b>候选人在某头部互联网公司主导过 2 个 LLM 落地项目，覆盖<b
                  >数据清洗 → 微调 → 推理优化 → 线上灰度</b
                >全链路，其中对话式客服模型日均调用量约 320 万次。
                <div class="cite">
                  <span class="n">1</span>项目经历 · 2023.04–2024.11 · 主导角色
                </div>
                <div class="cite">
                  <span class="n">2</span>技能标签 · LLM 微调 / LoRA / vLLM 推理优化
                </div>
              </div>
            </div>
          </div>
          <div class="ask-bar" style="margin-top: 14px">
            <input v-model="actions.question.value" placeholder="继续追问这位候选人的档案…" />
            <el-button class="btn primary sm" @click="actions.open('发送')">发送</el-button>
          </div>
        </div>

        <div class="card">
          <div class="card-head"><h3>档案完整度分布</h3></div>
          <div class="kpi-line">
            <span class="k">完整（≥90%）</span
            ><span class="v" style="color: var(--ok)">8,214 人</span>
          </div>
          <div class="kpi-line">
            <span class="k">较完整（70–90%）</span
            ><span class="v" style="color: var(--brand)">3,102 人</span>
          </div>
          <div class="kpi-line">
            <span class="k">待补充（&lt;70%）</span
            ><span class="v" style="color: var(--warn)">1,170 人</span>
          </div>
        </div>
      </div>
    </div>
    <ModuleWorkspace :sections="['人才档案', '人才标签', '人才能力分析']" /><ActionDialog
      :actions="actions"
    />
    <EvidencePanel mode="talent" />
  </section>
</template>
