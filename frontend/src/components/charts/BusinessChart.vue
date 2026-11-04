<script setup lang="ts">
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart, PieChart, RadarChart, FunnelChart, GaugeChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
use([
  CanvasRenderer,
  BarChart,
  LineChart,
  PieChart,
  RadarChart,
  FunnelChart,
  GaugeChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
])
const props = withDefaults(
  defineProps<{
    kind: 'bar' | 'line' | 'pie' | 'radar' | 'funnel' | 'gauge'
    labels?: string[]
    values?: number[]
  }>(),
  {
    labels: () => ['技术深度', '工程能力', '业务理解', '协作沟通', '学习潜力'],
    values: () => [94, 88, 81, 78, 92],
  },
)
const option = computed(() => {
  const base = {
    color: ['#3b82f6', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b'],
    tooltip: {},
    textStyle: { fontFamily: 'Microsoft YaHei', color: '#64748b' },
  }
  if (props.kind === 'radar')
    return {
      ...base,
      radar: { indicator: props.labels.map((name) => ({ name, max: 100 })), radius: '65%' },
      series: [{ type: 'radar', data: [{ value: props.values }], areaStyle: { opacity: 0.2 } }],
    }
  if (props.kind === 'pie' || props.kind === 'funnel')
    return {
      ...base,
      series: [
        {
          type: props.kind,
          radius: ['45%', '70%'],
          data: props.values.map((value, i) => ({ value, name: props.labels[i] })),
        },
      ],
    }
  if (props.kind === 'gauge')
    return {
      ...base,
      series: [
        {
          type: 'gauge',
          progress: { show: true },
          data: [{ value: props.values[0], name: '完成率' }],
        },
      ],
    }
  return {
    ...base,
    grid: { left: 40, right: 16, top: 20, bottom: 32 },
    xAxis: { type: 'category', data: props.labels },
    yAxis: { type: 'value' },
    series: [
      {
        type: props.kind,
        data: props.values,
        barMaxWidth: 38,
        itemStyle: { borderRadius: [7, 7, 0, 0] },
        smooth: true,
      },
    ],
  }
})
</script>
<template>
  <div>
    <p class="empty-note">图表说明：原型演示数据</p>
    <VChart class="business-chart" :option="option" autoresize />
  </div>
</template>
