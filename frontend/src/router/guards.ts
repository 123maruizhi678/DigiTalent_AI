import type { Router } from 'vue-router'
import { useUserStore } from '@/stores/modules/user'
export function installGuards(router: Router) {
  router.beforeEach((to) => {
    document.title = `${String(to.meta.title)} · AI 数字化人才平台`
    // 演示会话仅用于原型导航；真实认证和授权由后端逐请求校验。
    if (to.meta.requiresAuth && !useUserStore().demoSession && !useUserStore().authenticated)
      return '/login'
    return true
  })
}
