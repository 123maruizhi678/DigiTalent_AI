<script setup lang="ts">
import { services } from '@/config/technology'
import EvidencePanel from '@/components/business/EvidencePanel.vue'
import ModuleWorkspace from '@/components/business/ModuleWorkspace.vue'
import { computed, ref } from 'vue'
import { useLocalActions } from '@/utils/localActions'
import ActionDialog from '@/components/business/ActionDialog.vue'
import DemoTable from '@/components/business/DemoTable.vue'
const actions = useLocalActions()
const chips = ref<string[]>([])
function toggle(value: string) {
  chips.value = chips.value.includes(value)
    ? chips.value.filter((x) => x !== value)
    : [...chips.value, value]
}
const tables = [
  {
    columns: ['候选人', '应聘岗位', '匹配分', '核心标签', '解析状态', '操作'],
    rows: [
      [
        '陈 * 宇 硕士 · 6 年经验 · 浙江大学',
        '高级算法工程师',
        '94',
        'LLM 微调 RAG PyTorch',
        '解析完成',
        '查看画像',
      ],
      [
        '李 * 婷 本科 · 4 年经验 · 武汉大学',
        '数据分析师 P6',
        '88',
        'SQL 指标体系',
        '解析完成',
        '查看画像',
      ],
      [
        '王 * 峰 硕士 · 8 年经验 · 清华大学',
        'AI 产品经理',
        '76',
        'B 端产品 AI 落地',
        '解析中 62%',
        '查看画像',
      ],
      [
        '赵 * 涵 博士 · 3 年经验 · 上海交通大学',
        '高级算法工程师',
        '91',
        '多模态 CV',
        '扫描件 · 需复核',
        '人工校验',
      ],
    ],
  },
]
const filteredTable = computed(() => ({
  ...tables[0]!,
  rows: tables[0]!.rows.filter((row) => {
    const jobs = chips.value.filter((c) =>
      ['高级算法工程师', '数据分析师 P6', 'AI 产品经理', '后端开发'].includes(c),
    )
    return (
      (!jobs.length || jobs.includes(row[1]!)) &&
      (!chips.value.includes('匹配分 ≥ 80') || Number(row[2]) >= 80) &&
      (!chips.value.includes('已解析') || row[4] === '解析完成') &&
      (!chips.value.includes('待人工复核') || row[4]!.includes('复核')) &&
      (!chips.value.includes('3 年以上经验') || Number(row[0]?.match(/(\d+) 年/)?.[1]) > 3) &&
      (!chips.value.includes('已查重') || row[4] === '解析完成')
    )
  }),
}))
</script>
<template>
  <section class="page active">
    <div class="page-head">
      <div>
        <h1>简历智能筛选</h1>
        <p>全格式解析（PDF / Word / 图片 / 扫描件）· 向量级标签画像 · 语义化检索 · 智能查重合并</p>
      </div>
      <div class="head-actions">
        <el-button class="btn" @click="actions.open('批量导入')">批量导入</el-button>
        <el-button class="btn primary" @click="actions.open('+ 上传简历')">+ 上传简历</el-button>
      </div>
    </div>

    <div class="grid-3">
      <div class="card">
        <div class="gauge">
          <div class="gl">解析准确率（目标 ≥99%）</div>
          <div class="gv">99.2<small>%</small></div>
          <div class="progress green"><i style="width: 99%"></i></div>
        </div>
      </div>
      <div class="card">
        <div class="gauge">
          <div class="gl">今日待解析队列</div>
          <div class="gv">128<small>份</small></div>
          <div class="progress amber"><i style="width: 46%"></i></div>
        </div>
      </div>
      <div class="card">
        <div class="gauge">
          <div class="gl">重复简历合并命中</div>
          <div class="gv">37<small>组</small></div>
          <div class="progress"><i style="width: 62%"></i></div>
        </div>
      </div>
    </div>

    <div class="card" style="margin-bottom: 14px">
      <div class="card-head">
        <h3>筛选条件</h3>
        <el-button class="btn sm" @click="chips = []">重置</el-button>
      </div>
      <div class="chips" style="margin-bottom: 12px">
        <button
          class="chip"
          :class="{ on: chips.includes('全部岗位') }"
          @click="toggle('全部岗位')"
        >
          全部岗位
        </button>
        <button
          class="chip"
          :class="{ on: chips.includes('高级算法工程师') }"
          @click="toggle('高级算法工程师')"
        >
          高级算法工程师
        </button>
        <button
          class="chip"
          :class="{ on: chips.includes('数据分析师 P6') }"
          @click="toggle('数据分析师 P6')"
        >
          数据分析师 P6
        </button>
        <button
          class="chip"
          :class="{ on: chips.includes('AI 产品经理') }"
          @click="toggle('AI 产品经理')"
        >
          AI 产品经理
        </button>
        <button
          class="chip"
          :class="{ on: chips.includes('后端开发') }"
          @click="toggle('后端开发')"
        >
          后端开发
        </button>
      </div>
      <div class="chips">
        <button
          class="chip"
          :class="{ on: chips.includes('匹配分 ≥ 80') }"
          @click="toggle('匹配分 ≥ 80')"
        >
          匹配分 ≥ 80
        </button>
        <button class="chip" :class="{ on: chips.includes('已解析') }" @click="toggle('已解析')">
          已解析
        </button>
        <button
          class="chip"
          :class="{ on: chips.includes('待人工复核') }"
          @click="toggle('待人工复核')"
        >
          待人工复核
        </button>
        <button
          class="chip"
          :class="{ on: chips.includes('985 / 211') }"
          @click="toggle('985 / 211')"
        >
          985 / 211
        </button>
        <button
          class="chip"
          :class="{ on: chips.includes('3 年以上经验') }"
          @click="toggle('3 年以上经验')"
        >
          3 年以上经验
        </button>
        <button class="chip" :class="{ on: chips.includes('已查重') }" @click="toggle('已查重')">
          已查重
        </button>
      </div>
    </div>

    <div class="card" style="padding: 0; overflow: hidden">
      <DemoTable :data="filteredTable" @action="actions.open" />
    </div>

    <div class="grid-3" style="margin-top: 14px">
      <div class="card">
        <div class="card-head"><h3>文档解析链路</h3></div>
        <div
          v-for="service in services.filter((s) => ['MinerU', 'Milvus'].includes(s.name))"
          :key="service.name"
          class="kpi-line"
        >
          <span class="k">{{ service.name }}</span
          ><span class="tag gray">{{ service.status }}</span>
        </div>
        <p class="empty-note">部署与版本信息见系统技术状态与服务监控。</p>
      </div>
      <div class="card">
        <div class="card-head">
          <h3>解析失败归因</h3>
          <span class="tag gray">近 7 日</span>
        </div>
        <div class="kpi-line"><span class="k">扫描件模糊</span><span class="v">14 份</span></div>
        <div class="kpi-line"><span class="k">非标准表格</span><span class="v">9 份</span></div>
        <div class="kpi-line"><span class="k">加密 PDF</span><span class="v">4 份</span></div>
        <div class="kpi-line"><span class="k">其他</span><span class="v">2 份</span></div>
      </div>
      <div class="card">
        <div class="card-head">
          <h3>查重合并</h3>
          <span class="tag violet">向量相似度</span>
        </div>
        <div class="kpi-line">
          <span class="k">相似度 ≥0.95 自动合并</span><span class="v">21 组</span>
        </div>
        <div class="kpi-line">
          <span class="k">0.85–0.95 待确认</span><span class="v">16 组</span>
        </div>
        <div class="kpi-line">
          <span class="k">合并节省人工</span
          ><span class="v" style="color: var(--ok)">≈ 6.5 分</span>
        </div>
      </div>
    </div>
    <ModuleWorkspace :sections="['候选人管理', '招聘流程管理']" /><ActionDialog
      :actions="actions"
    />
    <EvidencePanel mode="resume" />
  </section>
</template>
