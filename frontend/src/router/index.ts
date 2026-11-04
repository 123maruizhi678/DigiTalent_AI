import { createRouter, createWebHashHistory } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'
import { modules, pageLoaders } from './routes'
import { installGuards } from './guards'
const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/login',
      component: () => import('@/views/system/LoginView.vue'),
      meta: { title: '演示登录' },
    },
    {
      path: '/',
      component: MainLayout,
      redirect: '/dashboard',
      children: Object.entries(pageLoaders).map(([id, component]) => ({
        path: id,
        component,
        meta: {
          requiresAuth: true,
          title: modules.flatMap((g) => g.items).find((x) => x[0] === id)?.[1] ?? id,
        },
      })),
    },
    { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
  ],
})
installGuards(router)
export default router
