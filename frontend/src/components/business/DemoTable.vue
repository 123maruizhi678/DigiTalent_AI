<script setup lang="ts">
import { computed, ref, watch } from 'vue'
const props = defineProps<{ data: { columns: string[]; rows: string[][] } }>()
const emit = defineEmits<{ action: [label: string] }>()
const search = ref(''),
  page = ref(1),
  size = ref(3)
const filtered = computed(() =>
  props.data.rows.filter((row) => row.join(' ').toLowerCase().includes(search.value.toLowerCase())),
)
const rows = computed(() =>
  filtered.value.slice((page.value - 1) * size.value, page.value * size.value),
)
watch([search, size, () => props.data.rows], () => {
  page.value = 1
})
</script>
<template>
  <div class="demo-table">
    <p class="empty-note">表格说明：本地原型演示数据。</p>
    <el-input
      v-model="search"
      clearable
      placeholder="搜索表格内容"
      aria-label="搜索表格内容"
    /><el-table :data="rows" style="width: 100%"
      ><el-table-column
        v-for="(label, index) in data.columns"
        :key="index"
        :label="label"
        :min-width="label === '操作' ? 110 : 140"
        ><template #default="scope"
          ><el-button
            v-if="label === '操作'"
            size="small"
            @click="emit('action', `${scope.row[index]}：${scope.row[0]}`)"
            >{{ scope.row[index] }}</el-button
          ><span v-else>{{ scope.row[index] }}</span></template
        ></el-table-column
      ></el-table
    ><el-pagination
      v-model:current-page="page"
      v-model:page-size="size"
      :page-sizes="[3, 5, 10]"
      :total="filtered.length"
      layout="total, sizes, prev, pager, next"
    />
  </div>
</template>
