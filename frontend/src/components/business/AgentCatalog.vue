<script setup lang="ts">
defineProps<{ compact?: boolean }>()
import { agents } from '@/config/agents'
</script>
<template>
  <div class="grid-4" :class="{ 'agent-compact': compact }">
    <div v-for="agent in agents" :key="agent.id" class="card">
      <div class="agent-ico">{{ agent.name.slice(0, 2) }}</div>
      <h3>{{ agent.name }}</h3>
      <p class="empty-note">{{ agent.description }}</p>
      <span class="tag gray">能力定义 · 未连接</span>
    </div>
  </div>
</template>

<style scoped>
.agent-compact {
  grid-template-columns: 1fr;
  gap: 4px;
}
.agent-compact .card {
  box-shadow: none;
  padding: 10px;
  border: 0;
}
.agent-compact .agent-ico {
  display: none;
}
.agent-compact h3 {
  margin: 0;
}
.agent-compact p {
  margin: 5px 0;
}
</style>
