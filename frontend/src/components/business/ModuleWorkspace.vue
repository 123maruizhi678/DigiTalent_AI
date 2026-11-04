<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useWorkspaceStore } from '@/stores/modules/workspace'
const props = defineProps<{ sections: string[] }>()
const store = useWorkspaceStore()
const active = ref(props.sections[0]!)
const keyword = ref(''),
  dialog = ref(false),
  editing = ref<number | null>(null),
  error = ref('')
const form = reactive({ name: '', detail: '', status: '启用' })
const rows = computed(() =>
  store.list(active.value).filter((r) => (r.name + r.detail + r.status).includes(keyword.value)),
)
function open(id?: number) {
  const row = rows.value.find((r) => r.id === id)
  editing.value = id ?? null
  Object.assign(form, row ?? { name: '', detail: '', status: '启用' })
  error.value = ''
  dialog.value = true
}
function save() {
  if (!form.name.trim() || !form.detail.trim()) {
    error.value = '名称与配置内容不能为空'
    return
  }
  store.save(active.value, editing.value, { ...form })
  dialog.value = false
}
async function remove(id: number) {
  try {
    await ElMessageBox.confirm('删除这条本地演示记录？', '删除确认')
    store.remove(active.value, id)
  } catch {
    /* 取消不改变记录 */
  }
}
function run(id: number) {
  store.status(active.value, id, '已完成（模拟）')
  ElMessage.success('本地模拟完成，未调用真实服务')
}
</script>
<template>
  <div class="card module-workspace">
    <h3>业务功能演示</h3>
    <p class="empty-note">以下为可编辑的本地示例，配置与执行结果不代表真实业务服务。</p>
    <el-tabs v-model="active"
      ><el-tab-pane v-for="section in sections" :key="section" :name="section" :label="section"
    /></el-tabs>
    <div class="workspace-toolbar">
      <el-input v-model="keyword" clearable placeholder="按名称、配置或状态筛选" /><el-button
        type="primary"
        @click="open()"
        >新增{{ active }}</el-button
      >
    </div>
    <el-table :data="rows"
      ><el-table-column prop="name" label="名称" min-width="160" /><el-table-column
        prop="detail"
        label="配置 / 内容"
        min-width="200"
      /><el-table-column prop="status" label="状态" min-width="120" /><el-table-column
        label="操作"
        min-width="230"
        ><template #default="scope"
          ><el-button size="small" @click="open(scope.row.id)">编辑</el-button
          ><el-button size="small" @click="run(scope.row.id)">模拟执行</el-button
          ><el-button size="small" type="danger" plain @click="remove(scope.row.id)"
            >删除</el-button
          ></template
        ></el-table-column
      ></el-table
    ><el-empty v-if="!rows.length" description="没有匹配记录" /><el-dialog
      v-model="dialog"
      :title="active + '配置'"
      width="min(560px,92vw)"
      ><el-form label-position="top"
        ><el-form-item label="名称" :error="error"
          ><el-input v-model="form.name" maxlength="80" /></el-form-item
        ><el-form-item label="配置内容 / 描述"
          ><el-input v-model="form.detail" type="textarea" :rows="5" /></el-form-item
        ><el-form-item label="状态"
          ><el-select v-model="form.status"
            ><el-option
              v-for="status in ['启用', '停用', '草稿', '待执行']"
              :key="status"
              :value="status"
              :label="status" /></el-select></el-form-item></el-form
      ><template #footer
        ><el-button @click="dialog = false">取消</el-button
        ><el-button type="primary" @click="save">保存</el-button></template
      ></el-dialog
    >
  </div>
</template>
