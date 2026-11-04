<script setup lang="ts">
import { ref } from 'vue'
import { candidateEvidence as evidence } from '@/config/evidence'
defineProps<{ mode: 'resume' | 'match' | 'talent' | 'exam' }>()
const open = ref(false),
  review = ref('待人工复核')
</script>
<template>
  <div class="card module-workspace">
    <div class="card-head">
      <h3>
        {{
          {
            resume: '简历解析结果',
            match: '匹配依据与分项得分',
            talent: 'AI 问答证据来源',
            exam: '测评与面试评分依据',
          }[mode]
        }}
      </h3>
      <el-button @click="open = true">查看证据示例</el-button>
    </div>
    <p class="empty-note">
      独立追溯样例 · {{ evidence.id }} · {{ evidence.name }} ·
      模拟结果；用于展示追溯设计，不代表页面其他候选人的证据。
    </p>
    <el-drawer v-model="open" title="人才数据证据追溯 · 模拟结果" size="min(760px, 94vw)"
      ><p>{{ evidence.id }} · {{ evidence.name }}</p>
      <template v-if="mode === 'resume'"
        ><el-descriptions :column="1" border
          ><el-descriptions-item
            v-for="[label, value] in [
              ['原始简历信息', evidence.resume + ' ' + evidence.original],
              ['结构化字段', evidence.fields],
              ['技能提取结果', evidence.skills],
              ['工作经历', evidence.work],
              ['项目经历', evidence.project],
              ['解析异常', evidence.anomaly],
            ]"
            :key="label"
            :label="label"
            >{{ value }}</el-descriptions-item
          ></el-descriptions
        >
        <p>人工复核状态（仅当前会话）</p>
        <el-select v-model="review"
          ><el-option
            v-for="status in ['待人工复核', '已复核', '需补充资料']"
            :key="status"
            :value="status" /></el-select
      ></template>
      <template v-if="mode === 'match'"
        ><p>岗位：高级算法工程师 · 模拟总分 81 / 100</p>
        <el-table :data="evidence.matching"
          ><el-table-column
            v-for="[prop, label] in [
              ['requirement', '岗位要求'],
              ['experience', '候选人对应经历'],
              ['basis', '匹配依据'],
              ['gap', '不匹配或待验证原因'],
              ['score', '分项得分'],
            ]"
            :key="prop"
            :prop="prop"
            :label="label"
            min-width="140" /></el-table
      ></template>
      <template v-if="mode === 'talent'"
        ><h3>问：候选人是否具备 RAG 项目经验？</h3>
        <p>
          模拟回答：简历记载召回与重排经验，项目规模尚需核实。[项目经历 / DEMO-C001 / 第 2 页]
        </p></template
      >
      <template v-if="mode === 'exam'"
        ><h3>测评结果与能力分析依据</h3>
        <p>
          DEMO-AS001 技术题 1–10 答对 9 题，每题 10 分，模拟得分 90 /
          100。该分数仅用于技术知识维度，不能推断综合能力。
        </p>
        <h3>面试评价记录</h3>
        <p>
          DEMO-IV001：能解释召回与重排；缺少分布式训练规模说明。评价依据为示例问答记录，建议补充项目材料。
        </p></template
      >
      <h3>来源定位与原文摘录</h3>
      <el-table :data="evidence.sources"
        ><el-table-column prop="source" label="证据来源" /><el-table-column
          prop="locator"
          label="记录 / 位置"
          min-width="180" /><el-table-column
          prop="excerpt"
          label="原文摘录（模拟）"
          min-width="200"
      /></el-table>
      <p class="empty-note">
        无真实文档检索或模型推理；来源仅为本地构造样例，尚未验证真实性。
      </p></el-drawer
    >
  </div>
</template>
