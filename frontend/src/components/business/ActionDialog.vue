<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import type { FormInstance } from 'element-plus'
import type { LocalActions } from '@/utils/localActions'
const { actions } = defineProps<{ actions: LocalActions }>()
const form = ref<FormInstance>()
const model = reactive({ name: '', detail: '' })
watch(actions.visible, (value) => {
  if (value) {
    model.name = actions.name.value
    model.detail = actions.detail.value
  }
})
async function save() {
  if (!(await form.value?.validate().catch(() => false))) return
  actions.commit(model.name, model.detail)
}
</script>
<template>
  <el-dialog
    :model-value="actions.visible.value"
    :title="actions.title.value + ' · 本地演示'"
    width="min(580px, 92vw)"
    destroy-on-close
    @close="actions.close"
  >
    <el-alert
      title="仅登记本地演示记录，不执行 AI、文件解析或后端任务。刷新后清空。"
      type="info"
      :closable="false"
    />
    <el-form ref="form" :model="model" label-position="top"
      ><el-form-item
        label="名称 / 操作对象"
        prop="name"
        :rules="[{ required: true, whitespace: true, message: '请输入名称', trigger: 'blur' }]"
        ><el-input v-model="model.name" maxlength="80" /></el-form-item
      ><el-form-item label="配置 / 备注"
        ><el-input v-model="model.detail" type="textarea" :rows="4" /></el-form-item
    ></el-form>
    <template #footer
      ><el-button @click="actions.close">取消</el-button
      ><el-button type="primary" @click="save">保存演示记录</el-button></template
    >
  </el-dialog>
  <div v-if="actions.store.records.length" class="card local-records">
    <h3>本地操作记录</h3>
    <div v-for="record in actions.store.records" :key="record.id" class="kpi-line">
      <span>{{ record.type }} · {{ record.name }}</span
      ><span>{{ record.detail || record.status }}</span>
    </div>
  </div>
</template>
