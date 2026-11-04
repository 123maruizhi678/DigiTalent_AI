<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Bell,
  Fold,
  Setting,
  Grid,
  Document,
  User,
  Tickets,
  Cpu,
  Monitor,
  DataAnalysis,
} from '@element-plus/icons-vue'
import { filterMenus } from '@/router/routes'
import { useUserStore } from '@/stores/modules/user'
const route = useRoute(),
  router = useRouter(),
  user = useUserStore()
const search = ref(''),
  notifications = ref(false),
  settings = ref(false)
const icons = [Grid, Document, User, Tickets, Cpu, Monitor, DataAnalysis, Setting]
const menus = computed(() =>
  filterMenus()
    .map((g) => ({
      ...g,
      items: g.items.filter((x) => x[1]!.includes(search.value) || g.title.includes(search.value)),
    }))
    .filter((g) => g.items.length),
)
function command(value: string) {
  if (value === 'logout') {
    user.logout()
    router.push('/login')
  } else settings.value = true
}
</script>
<template>
  <div class="app" :class="{ collapsed: user.collapsed }">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-logo">AI</div>
        <div class="brand-copy">
          <div class="brand-name">AI 数字化人才平台</div>
          <div class="brand-sub">AI 原生 · 企业级</div>
        </div>
      </div>
      <el-menu
        :default-active="route.path"
        :collapse="user.collapsed"
        router
        background-color="transparent"
        text-color="#94a3b8"
        active-text-color="#fff"
        class="nav"
        ><el-sub-menu v-for="(group, index) in menus" :key="group.title" :index="group.title"
          ><template #title
            ><el-icon><component :is="icons[index]" /></el-icon
            ><span>{{ group.title }}</span></template
          ><el-menu-item v-for="[id, title] in group.items" :key="id" :index="'/' + id">{{
            title
          }}</el-menu-item></el-sub-menu
        ></el-menu
      >
      <div class="sidebar-foot">
        <div class="user-chip">
          <div class="avatar">管</div>
          <div class="brand-copy">
            <div class="u-name">{{ user.name }}</div>
            <div class="u-role">本地原型演示</div>
          </div>
        </div>
      </div>
    </aside>
    <div class="main">
      <header class="topbar">
        <div class="crumb">
          <el-button
            :icon="Fold"
            circle
            aria-label="折叠菜单"
            @click="user.collapsed = !user.collapsed"
          /><span
            >AI 数字化人才平台 / <b>{{ route.meta.title }}</b></span
          >
        </div>
        <div class="top-actions">
          <el-input
            v-model="search"
            clearable
            placeholder="搜索页面 / 业务模块"
            class="search-input"
          /><el-button
            :icon="Bell"
            circle
            aria-label="通知"
            @click="notifications = true"
          /><el-button
            :icon="Setting"
            circle
            aria-label="模型供应商"
            @click="settings = true"
          /><el-dropdown @command="command"
            ><el-button>{{ user.name }} ▾</el-button
            ><template #dropdown
              ><el-dropdown-menu
                ><el-dropdown-item command="profile">个人信息</el-dropdown-item
                ><el-dropdown-item command="logout">退出演示</el-dropdown-item></el-dropdown-menu
              ></template
            ></el-dropdown
          >
        </div>
      </header>
      <main :key="route.path" class="content">
        <div class="demo-banner">当前展示为原型演示数据，尚未连接真实业务数据。统计卡片、表格、图表均为演示数据；AI 输出均为模拟结果。</div>
        <router-view />
      </main>
    </div>
    <el-drawer v-model="notifications" title="通知中心"
      ><el-empty description="暂无新通知（本地演示）" /></el-drawer
    ><el-dialog v-model="settings" title="用户与模型信息" width="min(520px, 90vw)"
      ><p>当前用户：{{ user.name }}</p>
      <p>模型供应商：未连接。真实认证、权限校验与模型配置由后续后端提供。</p></el-dialog
    >
  </div>
</template>
