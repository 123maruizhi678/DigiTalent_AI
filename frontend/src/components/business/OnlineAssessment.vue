<script setup lang="ts">
import { reactive, ref } from 'vue'
const answers = reactive({ single: '', multiple: [] as string[], judge: '', blank: '', short: '' })
const result = ref(''),
  submitted = ref(false)
function submit() {
  if (
    !answers.single ||
    !answers.multiple.length ||
    !answers.judge ||
    !answers.blank.trim() ||
    !answers.short.trim()
  ) {
    result.value = '请完成全部五道题后提交'
    return
  }
  submitted.value = true
  const score =
    (answers.single === 'B' ? 20 : 0) +
    (answers.multiple.length === 2 &&
    answers.multiple.includes('A') &&
    answers.multiple.includes('C')
      ? 20
      : 0) +
    (answers.judge === '正确' ? 20 : 0) +
    (answers.blank.trim().toLowerCase() === 'rag' ? 20 : 0)
  result.value = `客观题得分：${score}/80；简答题待人工评价（20分），本次为本地演示。`
}
function reset() {
  submitted.value = false
  result.value = ''
}
</script>
<template>
  <div class="card module-workspace">
    <h3>在线测评 · 五种题型演示</h3>
    <el-form label-position="top" :disabled="submitted"
      ><el-form-item label="1. 单选：哪种方法用于参数高效微调？"
        ><el-radio-group v-model="answers.single"
          ><el-radio value="A">K-means</el-radio><el-radio value="B">LoRA</el-radio
          ><el-radio value="C">PCA</el-radio></el-radio-group
        ></el-form-item
      ><el-form-item label="2. 多选：哪些属于检索增强生成的常见步骤？"
        ><el-checkbox-group v-model="answers.multiple"
          ><el-checkbox value="A">检索</el-checkbox><el-checkbox value="B">数据库删库</el-checkbox
          ><el-checkbox value="C">上下文生成</el-checkbox></el-checkbox-group
        ></el-form-item
      ><el-form-item label="3. 判断：前端隐藏菜单不能替代后端权限验证。"
        ><el-radio-group v-model="answers.judge"
          ><el-radio value="正确">正确</el-radio
          ><el-radio value="错误">错误</el-radio></el-radio-group
        ></el-form-item
      ><el-form-item label="4. 填空：检索增强生成的英文缩写是？"
        ><el-input v-model="answers.blank" /></el-form-item
      ><el-form-item label="5. 简答：如何验证岗位匹配结果的可靠性？"
        ><el-input v-model="answers.short" type="textarea" /></el-form-item></el-form
    ><el-alert
      v-if="result"
      :title="result"
      :type="submitted ? 'success' : 'warning'"
      :closable="false"
    /><el-button v-if="!submitted" type="primary" @click="submit">提交测评</el-button
    ><el-button v-else @click="reset">重新作答</el-button>
  </div>
</template>
