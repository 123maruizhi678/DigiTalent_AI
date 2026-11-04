<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/modules/user'
const name = ref('演示管理员'),
  error = ref(''),
  router = useRouter(),
  user = useUserStore()
function enter() {
  if (!name.value.trim()) {
    error.value = '请输入演示用户名'
    return
  }
  user.enterDemo(name.value.trim())
  router.push('/dashboard')
}
</script>
<template>
  <main class="login">
    <div class="card">
      <div class="brand-logo">AI</div>
      <h1>AI 数字化人才平台</h1>
      <p>账号由管理员创建或邀请，不开放自主注册。当前为本地演示入口，尚未接入真实身份认证。</p>
      <el-form @submit.prevent="enter"
        ><el-form-item label="演示用户名" :error="error"
          ><el-input v-model="name" @keyup.enter="enter" /></el-form-item
        ><el-button type="primary" @click="enter">进入演示</el-button></el-form
      >
    </div>
  </main>
</template>
