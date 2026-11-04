import { flushPromises, mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { nextTick, type Component } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { ElMessage, ElMessageBox } from 'element-plus'
import { registerElementPlus } from '@/plugins/element-plus'
import LoginView from '@/views/system/LoginView.vue'

vi.mock('@/components/charts/BusinessChart.vue', () => ({
  default: { template: '<div data-chart-stub />' },
}))

const pages = import.meta.glob<{ default: Component }>('../src/views/**/*.vue')
const layouts = import.meta.glob<{ default: Component }>('../src/layouts/*.vue')

async function options() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/:pathMatch(.*)*', component: { template: '<div />' } }],
  })
  await router.push('/')
  await router.isReady()
  return {
    attachTo: document.body,
    global: { plugins: [createPinia(), router, { install: registerElementPlus }] },
  }
}

afterEach(() => {
  ElMessage.closeAll()
  ElMessageBox.close()
  document.body.innerHTML = ''
  vi.restoreAllMocks()
})

describe('prototype compatibility with selected Element Plus components', () => {
  for (const [path, load] of Object.entries({ ...pages, ...layouts })) {
    it(`mounts ${path} without unresolved components or runtime errors`, async () => {
      const warnings = vi.spyOn(console, 'warn').mockImplementation(() => {})
      const errors = vi.spyOn(console, 'error').mockImplementation(() => {})
      const component = (await load()).default
      const wrapper = mount(component, await options())
      try {
        await flushPromises()
        expect(wrapper.exists()).toBe(true)
        expect(
          warnings.mock.calls.filter((args) =>
            /Failed to resolve component|Unhandled error/.test(args.join(' ')),
          ),
        ).toEqual([])
        expect(errors.mock.calls).toEqual([])
      } finally {
        wrapper.unmount()
      }
    })
  }

  it('keeps real form input and the demo login action working', async () => {
    const wrapper = mount(LoginView, await options())
    try {
      await wrapper.get('input').setValue('')
      await flushPromises()
      await wrapper.get('button').trigger('click')
      await vi.waitFor(() => expect(wrapper.text()).toContain('请输入演示用户名'))
      await wrapper.get('input').setValue('按需引入验证')
      await flushPromises()
      await wrapper.get('button').trigger('click')
      await flushPromises()
      expect(wrapper.vm.$router.currentRoute.value.path).toBe('/dashboard')
    } finally {
      wrapper.unmount()
    }
  })

  it('renders standalone message and confirmation services', async () => {
    const message = ElMessage.success({ message: '消息兼容性验证', duration: 0 })
    await nextTick()
    expect(document.querySelector('.el-message')?.textContent).toContain('消息兼容性验证')
    message.close()

    const confirmation = ElMessageBox.confirm('确认兼容性验证', '确认')
    await flushPromises()
    expect(document.querySelector('.el-message-box')?.textContent).toContain('确认兼容性验证')
    const confirm = document.querySelector<HTMLButtonElement>(
      '.el-message-box__btns .el-button--primary',
    )
    expect(confirm).not.toBeNull()
    confirm!.click()
    await expect(confirmation).resolves.toBe('confirm')
  })
})
