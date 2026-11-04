import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useDemoStore } from '@/stores/modules/demo'
export function useLocalActions() {
  const title = ref(''),
    visible = ref(false),
    question = ref(''),
    name = ref(''),
    detail = ref('')
  const store = useDemoStore()
  const router = useRouter()
  function open(action: string) {
    if (action.includes('导出')) {
      const blob = new Blob(
        [JSON.stringify({ notice: '原型演示数据', records: store.records }, null, 2)],
        { type: 'application/json' },
      )
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = '演示报告.json'
      a.click()
      URL.revokeObjectURL(url)
      return
    }
    if (action.includes('查看画像')) {
      router.push('/talent')
      return
    }
    if (action === '任务调度') {
      router.push('/employee')
      return
    }
    title.value = action
    name.value = ''
    detail.value = question.value
    visible.value = true
  }
  function close() {
    visible.value = false
  }
  function commit(n: string, d: string) {
    store.save(title.value, n, d)
    close()
  }
  return { title, visible, question, name, detail, open, store, close, commit }
}
export type LocalActions = ReturnType<typeof useLocalActions>
