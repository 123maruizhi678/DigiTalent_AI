import { defineStore } from 'pinia'
export const useDemoStore = defineStore('demo', {
  state: () => ({
    records: [] as { id: number; type: string; name: string; detail: string; status: string }[],
  }),
  actions: {
    save(type: string, name: string, detail: string) {
      this.records.unshift({ id: Date.now(), type, name, detail, status: '已保存（本地）' })
    },
  },
})
