import { defineStore } from 'pinia'
export const useUserStore = defineStore('user', {
  state: () => ({
    name: '系统管理员',
    authenticated: false,
    demoSession: false,
    roles: [] as string[],
    permissions: [] as string[],
    collapsed: false,
  }),
  actions: {
    enterDemo(name: string) {
      this.name = name
      this.demoSession = true
    },
    logout() {
      this.authenticated = false
      this.demoSession = false
      this.roles = []
      this.permissions = []
      this.name = '演示访客'
    },
  },
})
